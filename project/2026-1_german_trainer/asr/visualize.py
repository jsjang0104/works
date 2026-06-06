"""
training_history.json을 읽어 train/val Loss와 WER 커브를 시각화합니다.
출력: asr/training_curves.png

실행: python asr/visualize.py
"""

import json
import os

import matplotlib.pyplot as plt

BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
HISTORY_PATH = os.path.join(BASE_DIR, "training_history.json")
OUTPUT_PATH  = os.path.join(BASE_DIR, "training_curves.png")

with open(HISTORY_PATH, encoding="utf-8") as f:
    history = json.load(f)

epochs     = [h["epoch"]                for h in history]
train_loss = [h["train_loss"]           for h in history]
val_loss   = [h["val_loss"]             for h in history]
train_wer  = [h["train_wer"]  * 100     for h in history]
val_wer    = [h["val_wer"]    * 100     for h in history]

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
fig.suptitle("Whisper-tiny Fine-tuning · German Noun Phrases", fontsize=14)

# Loss
ax = axes[0]
ax.plot(epochs, train_loss, "o-", label="Train", color="steelblue")
ax.plot(epochs, val_loss,   "o-", label="Val",   color="tomato")
ax.set_xlabel("Epoch")
ax.set_ylabel("Loss (log scale)")
ax.set_title("Loss")
ax.set_yscale("log")
ax.legend()
ax.grid(True, alpha=0.3, which="both")

# WER
ax = axes[1]
ax.plot(epochs, train_wer, "o-", label="Train", color="steelblue")
ax.plot(epochs, val_wer,   "o-", label="Val",   color="tomato")
ax.set_xlabel("Epoch")
ax.set_ylabel("WER (%)")
ax.set_title("Word Error Rate")
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(OUTPUT_PATH, dpi=150)
print(f"[saved] {OUTPUT_PATH}")
plt.show()
