"""
파인튜닝된 Whisper 독일어 명사구 평가
데이터: data/noun-phrases/test/
결과:   data/noun-phrases/test/finetuned_result.json
"""

import os
import csv
import json
import re
from datetime import datetime

import torch
import soundfile as sf
from jiwer import wer
from transformers import WhisperForConditionalGeneration, WhisperProcessor

# ── 설정 ──────────────────────────────────────────────────────────────────────

LOG_INTERVAL = 100
THRESHOLD    = 0.15

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR   = os.path.join(BASE_DIR, "whisper-tiny-german")
DATA_DIR    = os.path.join(BASE_DIR, "..", "data", "noun-phrases", "test")
WAV_DIR     = os.path.join(DATA_DIR, "wav")
CSV_PATH    = os.path.join(DATA_DIR, "transcripts.csv")
RESULT_PATH = os.path.join(DATA_DIR, "finetuned_result.json")

# ── 모델 로드 ─────────────────────────────────────────────────────────────────

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"[device] {device}")

processor = WhisperProcessor.from_pretrained(MODEL_DIR)
model     = WhisperForConditionalGeneration.from_pretrained(MODEL_DIR).to(device)
model.eval()
print(f"[model] {MODEL_DIR} loaded")

# ── 데이터 로드 ───────────────────────────────────────────────────────────────

with open(CSV_PATH, encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

total = len(rows)
print(f"[data] {total} samples from {DATA_DIR}")

# ── 텍스트 정규화 ──────────────────────────────────────────────────────────────

def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\säöüß]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

# ── 추론 ──────────────────────────────────────────────────────────────────────

references, hypotheses, records = [], [], []

for i, row in enumerate(rows):
    audio, sr = sf.read(os.path.join(WAV_DIR, row["filename"]), dtype="float32")

    ref = normalize(row["transcript"])

    inputs = processor(audio, sampling_rate=sr, return_tensors="pt").to(device)
    with torch.no_grad():
        predicted_ids = model.generate(
            inputs.input_features,
            language="german",
            task="transcribe",
        )
    hyp = normalize(processor.batch_decode(predicted_ids, skip_special_tokens=True)[0])

    references.append(ref)
    hypotheses.append(hyp)
    records.append({"id": i, "file": row["filename"], "ref": ref, "hyp": hyp})

    if i < 5:
        print(f"\n[{i+1}]")
        print(f"  REF : {ref}")
        print(f"  HYP : {hyp}")

    if (i + 1) % LOG_INTERVAL == 0:
        partial = wer(references, hypotheses)
        print(f"[{i+1:>4}/{total}] WER so far: {partial*100:.2f}%")

# ── WER 계산 ──────────────────────────────────────────────────────────────────

score = wer(references, hypotheses)

print(f"\n{'─'*50}")
print(f"WER  : {score:.4f}  ({score*100:.2f}%)")
print(f"{'─'*50}")
if score > THRESHOLD:
    print(f"→ WER > {THRESHOLD*100:.0f}%: 추가 fine-tuning 권장")
else:
    print(f"→ WER ≤ {THRESHOLD*100:.0f}%: 모델 사용 가능")

# ── 결과 저장 ─────────────────────────────────────────────────────────────────

output = {
    "timestamp": datetime.now().isoformat(),
    "model": os.path.abspath(MODEL_DIR),
    "data_dir": os.path.abspath(DATA_DIR),
    "num_samples": total,
    "wer": round(score, 6),
    "wer_pct": round(score * 100, 2),
    "threshold": THRESHOLD,
    "samples": records,
}

with open(RESULT_PATH, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\n[saved] {RESULT_PATH}")
