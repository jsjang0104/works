"""
BLEURT scoring for klook_data.json (transformers-native, no TensorFlow 필요)

ref가 있는 항목에 대해 tgt(hypothesis)를 ref(reference)와 비교하여
BLEURT 점수를 계산하고 "BLEURT new" 필드를 업데이트합니다.

모델: Elron/bleurt-large-512 (HuggingFace Hub, PyTorch 기반)

Requirements:
    pip install transformers  (이미 설치되어 있어야 함)
"""

import json
import torch
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForSequenceClassification

INPUT_PATH  = Path(__file__).parent / "klook_data.json"
OUTPUT_PATH = Path(__file__).parent / "klook_data.json"

MODEL_NAME = "Elron/bleurt-large-512"


def main():
    with open(INPUT_PATH, encoding="utf-8") as f:
        data = json.load(f)

    targets = [
        (i, entry) for i, entry in enumerate(data)
        if entry.get("ref") and entry.get("tgt")
    ]
    print(f"Loaded {len(data)} entries, {len(targets)} have ref+tgt → scoring these")
    print(f"Model: {MODEL_NAME}\n")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = model.to(device)
    model.eval()

    references  = [entry["ref"] for _, entry in targets]
    predictions = [entry["tgt"] for _, entry in targets]

    with torch.no_grad():
        inputs = tokenizer(
            references, predictions,
            return_tensors="pt", padding=True, truncation=True, max_length=512
        ).to(device)
        scores = model(**inputs).logits.squeeze(-1).tolist()

    if isinstance(scores, float):
        scores = [scores]

    for (i, entry), score in zip(targets, scores):
        data[i]["BLEURT new"] = round(float(score), 6)
        print(f"  [{entry['type']:20s}] {entry['src'][:55]!r:58s} → {score:.4f}")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\nSaved → {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
