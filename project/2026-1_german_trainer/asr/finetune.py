"""
Whisper tiny 독일어 파인튜닝
데이터: data/noun-phrases/train/ (학습), data/noun-phrases/val/ (검증)
출력:   asr/whisper-tiny-german/
"""

import csv
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List

import numpy as np
import soundfile as sf
import torch
from torch.utils.data import Dataset
from transformers import (
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
    WhisperForConditionalGeneration,
    WhisperProcessor,
)
from jiwer import wer as jiwer_wer

# ── 설정 ──────────────────────────────────────────────────────────────────────

MODEL_ID    = "openai/whisper-tiny"
LANGUAGE    = "german"
TASK        = "transcribe"
SAMPLE_RATE = 16000

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
NP_DIR      = os.path.join(BASE_DIR, "..", "data", "noun-phrases")
TRAIN_DIR   = os.path.join(NP_DIR, "train")
VAL_DIR     = os.path.join(NP_DIR, "val")
OUTPUT_DIR  = os.path.join(BASE_DIR, "whisper-tiny-german")

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

# ── 모델 & 프로세서 로드 ──────────────────────────────────────────────────────

print(f"[model] Loading {MODEL_ID} ...")
processor = WhisperProcessor.from_pretrained(MODEL_ID, language=LANGUAGE, task=TASK)
model     = WhisperForConditionalGeneration.from_pretrained(MODEL_ID)
model.generation_config.language           = LANGUAGE
model.generation_config.task               = TASK
model.generation_config.forced_decoder_ids = None

# ── 데이터셋 로드 ─────────────────────────────────────────────────────────────

print("[data] Loading datasets ...")
train_dataset = GermanASRDataset(TRAIN_DIR, processor)
val_dataset   = GermanASRDataset(VAL_DIR,   processor)
print(f"[data] train={len(train_dataset)}, val={len(val_dataset)}")

# ── WER 평가 함수 ─────────────────────────────────────────────────────────────

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
    per_device_eval_batch_size=8,
    gradient_accumulation_steps=1,
    learning_rate=1e-5,
    warmup_steps=100,
    num_train_epochs=5,
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

trainer = Seq2SeqTrainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    data_collator=DataCollator(processor=processor),
    compute_metrics=compute_metrics,
    processing_class=processor.feature_extractor,
)

# ── 학습 시작 ─────────────────────────────────────────────────────────────────

print("[train] Starting fine-tuning ...")
trainer.train()

# ── 저장 ──────────────────────────────────────────────────────────────────────

print(f"[save] Saving model to {OUTPUT_DIR} ...")
trainer.save_model(OUTPUT_DIR)
processor.save_pretrained(OUTPUT_DIR)
print("Done.")
