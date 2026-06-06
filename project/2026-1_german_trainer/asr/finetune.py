"""
Whisper tiny 독일어 파인튜닝
데이터: data/noun-phrases/train/ (학습), data/noun-phrases/val/ (검증)
출력:   asr/whisper-tiny-german/
        asr/training_history.json
"""

import csv
import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List

import soundfile as sf
import torch
from torch.utils.data import DataLoader, Dataset
from transformers import (
    EarlyStoppingCallback,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
    TrainerCallback,
    WhisperForConditionalGeneration,
    WhisperProcessor,
)
from jiwer import wer as jiwer_wer

# ── 설정 ──────────────────────────────────────────────────────────────────────

MODEL_ID    = "openai/whisper-tiny"
LANGUAGE    = "german"
TASK        = "transcribe"
SAMPLE_RATE = 16000

BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
NP_DIR       = os.path.join(BASE_DIR, "..", "data", "noun-phrases")
TRAIN_DIR    = os.path.join(NP_DIR, "train")
VAL_DIR      = os.path.join(NP_DIR, "val")
OUTPUT_DIR   = os.path.join(BASE_DIR, "whisper-tiny-german")
HISTORY_PATH = os.path.join(BASE_DIR, "training_history.json")

EARLY_STOP_PATIENCE = 3  # val_wer가 N 에포크 연속 개선 없으면 중단

# ── 텍스트 정규화 ──────────────────────────────────────────────────────────────

def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\säöüß]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

# ── 데이터셋 ───────────────────────────────────────────────────────────────────

class GermanASRDataset(Dataset):
    def __init__(self, data_dir: str, processor: WhisperProcessor):
        self.wav_dir   = os.path.join(data_dir, "wav")
        self.processor = processor
        with open(os.path.join(data_dir, "transcripts.csv"), encoding="utf-8") as f:
            self.samples = list(csv.DictReader(f))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        row = self.samples[idx]
        audio, sr = sf.read(os.path.join(self.wav_dir, row["filename"]), dtype="float32")

        if sr != SAMPLE_RATE:
            import librosa
            audio = librosa.resample(audio, orig_sr=sr, target_sr=SAMPLE_RATE)

        input_features = self.processor(
            audio, sampling_rate=SAMPLE_RATE, return_tensors="pt"
        ).input_features[0]

        labels = self.processor.tokenizer(normalize(row["transcript"])).input_ids
        return {"input_features": input_features, "labels": labels}

# ── 데이터 콜레이터 ───────────────────────────────────────────────────────────

@dataclass
class DataCollator:
    processor: WhisperProcessor

    def __call__(self, features: List[Dict[str, Any]]) -> Dict[str, torch.Tensor]:
        input_features = [{"input_features": f["input_features"]} for f in features]
        batch = self.processor.feature_extractor.pad(input_features, return_tensors="pt")

        label_features = [{"input_ids": f["labels"]} for f in features]
        labels_batch   = self.processor.tokenizer.pad(label_features, return_tensors="pt")

        labels = labels_batch["input_ids"].masked_fill(
            labels_batch.attention_mask.ne(1), -100
        )
        if (labels[:, 0] == self.processor.tokenizer.bos_token_id).all().cpu().item():
            labels = labels[:, 1:]

        batch["labels"] = labels
        return batch

# ── 에포크별 메트릭 수집 콜백 ─────────────────────────────────────────────────

class EpochMetricsCallback(TrainerCallback):
    """매 에포크 평가 후 train/val loss+WER을 JSON으로 저장."""

    def __init__(self, train_dataset, processor, collator, save_path):
        self.train_dataset = train_dataset
        self.processor     = processor
        self.collator      = collator
        self.save_path     = save_path
        self.history       = []

    def on_evaluate(self, args, state, control, metrics, model=None, **kwargs):
        epoch = round(state.epoch)

        # train loss: 해당 에포크 구간 step loss 평균
        prev_epoch  = epoch - 1
        step_losses = [
            log["loss"] for log in state.log_history
            if "loss" in log
            and log.get("epoch", 0) > prev_epoch
            and log.get("epoch", 0) <= epoch
        ]
        avg_train_loss = round(sum(step_losses) / len(step_losses), 6) if step_losses else None

        # train WER: generate로 직접 계산 (trainer를 거치지 않아 콜백 재진입 없음)
        train_wer_score = self._compute_wer(model)

        entry = {
            "epoch":      epoch,
            "train_loss": avg_train_loss,
            "train_wer":  round(train_wer_score, 6),
            "val_loss":   round(metrics.get("eval_loss", 0), 6),
            "val_wer":    round(metrics.get("eval_wer",  0), 6),
        }
        self.history.append(entry)

        with open(self.save_path, "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)

        tl = f"{entry['train_loss']:.4f}" if entry["train_loss"] is not None else "N/A"
        print(
            f"\n[epoch {epoch:>2}] "
            f"train_loss={tl}  train_wer={entry['train_wer']*100:.2f}%  "
            f"val_loss={entry['val_loss']:.4f}  val_wer={entry['val_wer']*100:.2f}%"
        )

    def _compute_wer(self, model) -> float:
        device = next(model.parameters()).device
        loader = DataLoader(self.train_dataset, batch_size=16, collate_fn=self.collator)

        refs, hyps = [], []
        model.eval()
        with torch.no_grad():
            for batch in loader:
                input_features = batch["input_features"].to(device)
                labels         = batch["labels"].to(device)

                pred_ids = model.generate(
                    input_features,
                    language=LANGUAGE,
                    task=TASK,
                    max_new_tokens=225,
                )

                label_ids = labels.clone()
                label_ids[label_ids == -100] = self.processor.tokenizer.pad_token_id

                hyps.extend(self.processor.tokenizer.batch_decode(pred_ids,   skip_special_tokens=True))
                refs.extend(self.processor.tokenizer.batch_decode(label_ids,  skip_special_tokens=True))

        return float(jiwer_wer(refs, hyps))

# ── 모델 & 프로세서 로드 ──────────────────────────────────────────────────────

print(f"[model] Loading {MODEL_ID} ...")
processor = WhisperProcessor.from_pretrained(MODEL_ID, language=LANGUAGE, task=TASK)
model     = WhisperForConditionalGeneration.from_pretrained(MODEL_ID)
model.generation_config.language           = LANGUAGE
model.generation_config.task               = TASK
model.generation_config.forced_decoder_ids = None

# ── 데이터셋 & 콜레이터 ───────────────────────────────────────────────────────

print("[data] Loading datasets ...")
collator      = DataCollator(processor=processor)
train_dataset = GermanASRDataset(TRAIN_DIR, processor)
val_dataset   = GermanASRDataset(VAL_DIR,   processor)
print(f"[data] train={len(train_dataset)}, val={len(val_dataset)}")

# ── WER 평가 함수 (val, trainer 내부용) ───────────────────────────────────────

def compute_metrics(pred):
    pred_ids  = pred.predictions
    label_ids = pred.label_ids
    label_ids[label_ids == -100] = processor.tokenizer.pad_token_id

    pred_str  = processor.tokenizer.batch_decode(pred_ids,  skip_special_tokens=True)
    label_str = processor.tokenizer.batch_decode(label_ids, skip_special_tokens=True)

    return {"wer": jiwer_wer(label_str, pred_str)}

# ── 학습 설정 ─────────────────────────────────────────────────────────────────

training_args = Seq2SeqTrainingArguments(
    output_dir=OUTPUT_DIR,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    gradient_accumulation_steps=1,
    learning_rate=1e-5,
    warmup_steps=100,
    num_train_epochs=20,
    bf16=True,
    predict_with_generate=True,
    generation_max_length=225,
    eval_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    metric_for_best_model="wer",
    greater_is_better=False,
    logging_steps=50,
    dataloader_num_workers=4,
    report_to="none",
)

metrics_cb = EpochMetricsCallback(train_dataset, processor, collator, HISTORY_PATH)

trainer = Seq2SeqTrainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    data_collator=collator,
    compute_metrics=compute_metrics,
    processing_class=processor.feature_extractor,
    callbacks=[
        metrics_cb,
        EarlyStoppingCallback(early_stopping_patience=EARLY_STOP_PATIENCE),
    ],
)

# ── 학습 시작 ─────────────────────────────────────────────────────────────────

print("[train] Starting fine-tuning ...")
trainer.train()

# ── 저장 ──────────────────────────────────────────────────────────────────────

print(f"[save] Saving model to {OUTPUT_DIR} ...")
trainer.save_model(OUTPUT_DIR)
processor.save_pretrained(OUTPUT_DIR)
print(f"[history] {HISTORY_PATH}")
print("Done.")
