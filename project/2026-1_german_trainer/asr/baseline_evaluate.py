"""
Whisper tiny (원본) 독일어 명사구 평가
데이터: data/noun-phrases/test/
결과:   data/noun-phrases/test/baseline_result.json
"""

import os
import csv
import json
import re
from datetime import datetime

import whisper
import torch
import soundfile as sf
from jiwer import wer

# ── 설정 ──────────────────────────────────────────────────────────────────────

MODEL_SIZE   = "tiny"
LOG_INTERVAL = 100
THRESHOLD    = 0.15

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
DATA_DIR    = os.path.join(BASE_DIR, "..", "data", "noun-phrases", "test")
WAV_DIR     = os.path.join(DATA_DIR, "wav")
CSV_PATH    = os.path.join(DATA_DIR, "transcripts.csv")
RESULT_PATH = os.path.join(DATA_DIR, "baseline_result.json")

# ── 모델 로드 ─────────────────────────────────────────────────────────────────

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"[device] {device}")

model = whisper.load_model(MODEL_SIZE, device=device)
print(f"[model] whisper-{MODEL_SIZE} loaded")

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
    result = model.transcribe(audio, language="de", fp16=(device == "cuda"))
    hyp = normalize(result["text"])

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
    print(f"→ WER > {THRESHOLD*100:.0f}%: fine-tuning 권장")
else:
    print(f"→ WER ≤ {THRESHOLD*100:.0f}%: baseline 그대로 사용 가능")

# ── 결과 저장 ─────────────────────────────────────────────────────────────────

output = {
    "timestamp": datetime.now().isoformat(),
    "model": f"whisper-{MODEL_SIZE} (원본)",
    "data_dir": os.path.abspath(DATA_DIR),
    "num_samples": total,
    "wer": round(score, 6),
    "wer_pct": round(score * 100, 2),
    "threshold": THRESHOLD,
    "finetune_recommended": score > THRESHOLD,
    "samples": records,
}

with open(RESULT_PATH, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\n[saved] {RESULT_PATH}")
