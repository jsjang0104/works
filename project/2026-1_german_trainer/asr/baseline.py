"""
Whisper small 독일어 baseline 평가
데이터셋: Mozilla Common Voice (de)
지표: WER (Word Error Rate)
"""

import whisper
import torch
from datasets import load_dataset
from jiwer import wer
import re


# ── 설정 ──────────────────────────────────────────────────────────────────────

MODEL_SIZE   = "tiny"
DATASET_NAME = "mozilla-foundation/common_voice_11_0"
LANG         = "de"
SPLIT        = "validation"
NUM_SAMPLES  = 200   # 전체 쓰면 오래 걸리므로 일부만

# ── 모델 로드 ─────────────────────────────────────────────────────────────────

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"[device] {device}")

model = whisper.load_model(MODEL_SIZE, device=device)
print(f"[model] whisper-{MODEL_SIZE} loaded")

# ── 데이터 로드 ───────────────────────────────────────────────────────────────

dataset = load_dataset(
    DATASET_NAME, LANG,
    split=SPLIT,
    trust_remote_code=True,
)
dataset = dataset.select(range(min(NUM_SAMPLES, len(dataset))))
print(f"[data] {len(dataset)} samples from {DATASET_NAME}/{LANG}/{SPLIT}")

# ── 텍스트 정규화 ──────────────────────────────────────────────────────────────

def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\säöüß]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

# ── 추론 ──────────────────────────────────────────────────────────────────────

references, hypotheses = [], []

for i, sample in enumerate(dataset):
    audio = sample["audio"]
    ref   = normalize(sample["sentence"])

    result = model.transcribe(
        audio["array"].astype("float32"),
        language="de",
        fp16=(device == "cuda"),
    )
    hyp = normalize(result["text"])

    references.append(ref)
    hypotheses.append(hyp)

    if i < 5:  # 처음 5개 출력
        print(f"\n[{i+1}]")
        print(f"  REF : {ref}")
        print(f"  HYP : {hyp}")

# ── WER 계산 ──────────────────────────────────────────────────────────────────

score = wer(references, hypotheses)
print(f"\n{'─'*50}")
print(f"WER  : {score:.4f}  ({score*100:.2f}%)")
print(f"{'─'*50}")

THRESHOLD = 0.15
if score > THRESHOLD:
    print(f"→ WER > {THRESHOLD*100:.0f}%: fine-tuning 권장")
else:
    print(f"→ WER ≤ {THRESHOLD*100:.0f}%: baseline 그대로 사용 가능")
