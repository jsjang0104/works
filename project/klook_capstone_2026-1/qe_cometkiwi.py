"""
COMETKiwi-23-XL QE scoring for klook_data.json

ref가 있는 항목의 tgt에 대해 (src, tgt) 쌍으로 QE 점수를 계산하고
"cometKiwi" 필드를 업데이트합니다.

Requirements:
    pip install unbabel-comet
"""

import json
import torch
from pathlib import Path
from huggingface_hub import snapshot_download
from comet import load_from_checkpoint

INPUT_PATH  = Path(__file__).parent / "klook_data.json"
OUTPUT_PATH = Path(__file__).parent / "klook_data.json"

BATCH_SIZE = 16
MODEL_NAME = "Unbabel/wmt23-cometkiwi-da-xl"


def main():
    with open(INPUT_PATH, encoding="utf-8") as f:
        data = json.load(f)

    # ref가 있는 항목만 (tgt도 함께 있어야 함)
    targets = [
        (i, entry) for i, entry in enumerate(data)
        if entry.get("ref") and entry.get("tgt")
    ]
    print(f"Loaded {len(data)} entries, {len(targets)} have ref+tgt → scoring these")

    model_path = snapshot_download(repo_id=MODEL_NAME)
    model = load_from_checkpoint(model_path + "/checkpoints/model.ckpt")

    # COMETKiwi는 참조 없이 (src, mt) 쌍으로 QE
    pairs = [{"src": entry["src"], "mt": entry["tgt"]} for _, entry in targets]

    gpus = 1 if torch.cuda.is_available() else 0
    print(f"Scoring {len(pairs)} pairs with {MODEL_NAME} ...")
    output = model.predict(pairs, batch_size=BATCH_SIZE, gpus=gpus)

    for (i, entry), score in zip(targets, output.scores):
        data[i]["cometKiwi"] = round(float(score), 6)
        print(f"  [{entry['type']:20s}] {entry['src'][:55]!r:58s} → {score:.4f}")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\nSaved → {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
