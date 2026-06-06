"""
파인튜닝된 Whisper-tiny로 실제 발화 평가
데이터: data/human/{speaker}/wav/ + data/human/recording_list.csv
출력:   asr/final_result.json
        asr/final_eval.png

화자 그룹
  good : hw_ha, jk_hong, mk_cho, mc_park
  poor : js_jang, jw_choi

score 열이 채워진 경우 DA score vs WER / LL Spearman 상관관계를 추가로 계산합니다.
"""

import csv
import json
import os
import re
from collections import defaultdict
from datetime import datetime

import matplotlib.pyplot as plt
import soundfile as sf
import torch
from jiwer import wer as jiwer_wer
from scipy.stats import spearmanr
from transformers import WhisperForConditionalGeneration, WhisperProcessor

# ── 설정 ──────────────────────────────────────────────────────────────────────

LANGUAGE    = "german"
TASK        = "transcribe"
SAMPLE_RATE = 16000

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR   = os.path.join(BASE_DIR, "whisper-tiny-german")
HUMAN_DIR   = os.path.join(BASE_DIR, "..", "data", "human")
LIST_CSV    = os.path.join(HUMAN_DIR, "recording_list.csv")
RESULT_PATH = os.path.join(BASE_DIR, "final_result.json")
PLOT_PATH   = os.path.join(BASE_DIR, "final_eval.png")

GROUPS = {
    "hw_ha":   "good", "jk_hong": "good",
    "mk_cho":  "good", "mc_park": "good",
    "jw_kim":  "good",
    "js_jang": "poor", "jw_choi": "poor",
}
GROUP_COLOR = {"good": "steelblue", "poor": "tomato"}

# ── 텍스트 정규화 ──────────────────────────────────────────────────────────────

def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\säöüß]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

# ── 모델 로드 ─────────────────────────────────────────────────────────────────

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"[device] {device}")

processor = WhisperProcessor.from_pretrained(MODEL_DIR)
model     = WhisperForConditionalGeneration.from_pretrained(MODEL_DIR).to(device)
model.eval()
print(f"[model] {MODEL_DIR} loaded")

# ── 추론 & log-likelihood ──────────────────────────────────────────────────────

def transcribe(audio):
    inputs = processor(audio, sampling_rate=SAMPLE_RATE, return_tensors="pt").to(device)
    with torch.no_grad():
        pred_ids = model.generate(
            inputs.input_features, language=LANGUAGE, task=TASK,
        )
    return normalize(processor.batch_decode(pred_ids, skip_special_tokens=True)[0])

def log_likelihood(audio, ref_text):
    """per-token 평균 log-likelihood (높을수록 발음이 정답에 가까움)"""
    inputs    = processor(audio, sampling_rate=SAMPLE_RATE, return_tensors="pt").to(device)
    label_ids = processor.tokenizer(
        normalize(ref_text), return_tensors="pt"
    ).input_ids.to(device)
    with torch.no_grad():
        loss = model(input_features=inputs.input_features, labels=label_ids).loss
    return round(-loss.item(), 6)

# ── recording_list.csv 로드 ───────────────────────────────────────────────────

speaker_data = defaultdict(list)
with open(LIST_CSV, encoding="utf-8") as f:
    for row in csv.DictReader(f):
        score = int(row["score"]) if row.get("score", "").strip() else None
        speaker_data[row["speaker"]].append((row["KR"], row["DE"], score))

print(f"[data] {len(speaker_data)}명: {list(speaker_data.keys())}")

# ── 평가 루프 ─────────────────────────────────────────────────────────────────

all_refs, all_hyps = [], []
group_refs         = defaultdict(list)
group_hyps         = defaultdict(list)
speaker_results    = {}
all_scores, all_ll, all_sample_wer = [], [], []

for speaker, phrases in speaker_data.items():
    wav_dir = os.path.join(HUMAN_DIR, speaker, "wav")
    refs, hyps, records = [], [], []

    for i, (korean, german, score) in enumerate(phrases):
        wav_path = os.path.join(wav_dir, f"{i:04d}.wav")
        if not os.path.exists(wav_path):
            continue

        audio, _ = sf.read(wav_path, dtype="float32")
        ref = normalize(german)
        hyp = transcribe(audio)
        ll  = log_likelihood(audio, german)
        sample_wer = jiwer_wer([ref], [hyp])

        refs.append(ref)
        hyps.append(hyp)
        records.append({"id": i, "file": f"{i:04d}.wav", "KR": korean,
                        "ref": ref, "hyp": hyp,
                        "log_likelihood": ll, "sample_wer": round(sample_wer, 4),
                        "score": score})

        if score is not None:
            all_scores.append(score)
            all_ll.append(ll)
            all_sample_wer.append(sample_wer)

    speaker_wer = jiwer_wer(refs, hyps) if refs else None
    avg_ll      = round(sum(r["log_likelihood"] for r in records) / len(records), 6) if records else None
    group       = GROUPS.get(speaker, "unknown")

    speaker_results[speaker] = {
        "group": group, "num_samples": len(refs),
        "wer": round(speaker_wer, 6) if speaker_wer is not None else None,
        "wer_pct": round(speaker_wer * 100, 2) if speaker_wer is not None else None,
        "avg_log_likelihood": avg_ll,
        "records": records,
    }
    all_refs.extend(refs); all_hyps.extend(hyps)
    group_refs[group].extend(refs); group_hyps[group].extend(hyps)

    print(f"[{speaker}({group})] WER={speaker_wer*100:.2f}%  LL={avg_ll:.4f}" if speaker_wer else f"[{speaker}] 파일 없음")

overall_wer = jiwer_wer(all_refs, all_hyps) if all_refs else None
group_wer   = {g: jiwer_wer(group_refs[g], group_hyps[g]) for g in group_refs if group_refs[g]}
overall_ll  = round(sum(
    r["log_likelihood"] for s in speaker_results.values() for r in s["records"]
) / max(sum(s["num_samples"] for s in speaker_results.values()), 1), 6)

print(f"\n[overall] WER={overall_wer*100:.2f}%  LL={overall_ll:.4f}")
for g, w in group_wer.items():
    print(f"[{g}]  WER={w*100:.2f}%")

# ── DA score 상관관계 (score 존재 시) ─────────────────────────────────────────

correlation = {}
if len(all_scores) >= 3:
    r_ll,  p_ll  = spearmanr(all_scores, all_ll)
    r_wer, p_wer = spearmanr(all_scores, all_sample_wer)
    correlation = {
        "n": len(all_scores),
        "spearman_score_vs_ll":  {"r": round(r_ll,  4), "p": round(p_ll,  4)},
        "spearman_score_vs_wer": {"r": round(r_wer, 4), "p": round(p_wer, 4)},
    }
    print(f"\n[DA correlation] n={len(all_scores)}")
    print(f"  score vs LL  : r={r_ll:.4f}  p={p_ll:.4f}")
    print(f"  score vs WER : r={r_wer:.4f}  p={p_wer:.4f}")
else:
    print("\n[DA correlation] score 미입력 — 건너뜀")

# ── 결과 저장 ─────────────────────────────────────────────────────────────────

result = {
    "timestamp": datetime.now().isoformat(), "model": os.path.abspath(MODEL_DIR),
    "overall_wer": round(overall_wer, 6) if overall_wer else None,
    "overall_wer_pct": round(overall_wer * 100, 2) if overall_wer else None,
    "overall_log_likelihood": overall_ll,
    "group_wer": {g: round(w * 100, 2) for g, w in group_wer.items()},
    "da_correlation": correlation,
    "speakers": speaker_results,
}
with open(RESULT_PATH, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print(f"\n[saved] {RESULT_PATH}")

# ── 시각화 ────────────────────────────────────────────────────────────────────

speakers   = [s for s in speaker_results if speaker_results[s]["num_samples"] > 0]
wer_vals   = [speaker_results[s]["wer_pct"] or 0 for s in speakers]
ll_vals    = [speaker_results[s]["avg_log_likelihood"] or 0 for s in speakers]
bar_colors = [GROUP_COLOR.get(GROUPS.get(s, ""), "gray") for s in speakers]

n_plots = 4 if len(all_scores) >= 3 else 2
fig, axes = plt.subplots(1, n_plots, figsize=(6 * n_plots, 5))
if n_plots == 2:
    axes = list(axes)
fig.suptitle("Whisper-tiny (fine-tuned) · Human Speech Evaluation", fontsize=13)

for ax, vals, ylabel, title in [
    (axes[0], wer_vals, "WER (%)",           "Word Error Rate"),
    (axes[1], ll_vals,  "Avg Log-Likelihood", "Log-Likelihood"),
]:
    bars = ax.bar(speakers, vals, color=bar_colors, edgecolor="white", width=0.6)
    for g, c in GROUP_COLOR.items():
        ax.bar(0, 0, color=c, label=f"{g} speakers")
    for bar, val in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + (max(vals) - min(vals)) * 0.02,
                f"{val:.2f}", ha="center", va="bottom", fontsize=9)
    ax.set_xlabel("Speaker"); ax.set_ylabel(ylabel); ax.set_title(title)
    ax.legend(); ax.grid(axis="y", alpha=0.3)

if len(all_scores) >= 3:
    r_ll, _  = spearmanr(all_scores, all_ll)
    r_wer, _ = spearmanr(all_scores, all_sample_wer)

    ax = axes[2]
    ax.scatter(all_scores, all_ll, alpha=0.6, color="steelblue")
    ax.set_xlabel("DA Score"); ax.set_ylabel("Log-Likelihood")
    ax.set_title(f"Score vs LL  (ρ={r_ll:.3f})")
    ax.set_xticks([1, 2, 3]); ax.grid(alpha=0.3)

    ax = axes[3]
    ax.scatter(all_scores, [w * 100 for w in all_sample_wer], alpha=0.6, color="tomato")
    ax.set_xlabel("DA Score"); ax.set_ylabel("WER (%)")
    ax.set_title(f"Score vs WER  (ρ={r_wer:.3f})")
    ax.set_xticks([1, 2, 3]); ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig(PLOT_PATH, dpi=150)
plt.close()
print(f"[saved] {PLOT_PATH}")
