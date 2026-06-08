"""
ASR evaluation with the original Whisper-large-v3 (human data only)

Data:
  human : data/human/{speaker}/wav/ + data/human/recording_list.csv
          Real-world recordings, used to compare pronunciation-level groups
          (advanced/intermediate/basic). Every speaker recorded the same
          25 sentences, so content is controlled and only speaker/pronunciation
          differences vary.

Output: asr/eval/large_result_human.json
        asr/eval/large_eval_human.png

Speaker groups (human)
  advanced     : 01, 02, 03, 04, 05
  intermediate : 06, 07, 08
  basic        : 09, 10

If the score column is filled in, also computes the Spearman correlation
between DA score and WER / log-likelihood.
The DA score vs WER(%) boxplot drops extreme outliers based on the IQR.

Usage:
    python large_evaluate.py
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

# ── Settings ──────────────────────────────────────────────────────────────────

MODEL_ID    = "openai/whisper-large-v3"
LANGUAGE    = "german"
TASK        = "transcribe"
SAMPLE_RATE = 16000

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
DATA_DIR    = os.path.join(BASE_DIR, "..", "..", "data")

HUMAN_DIR   = os.path.join(DATA_DIR, "human")
LIST_CSV    = os.path.join(HUMAN_DIR, "recording_list.csv")

RESULT_PATH = os.path.join(BASE_DIR, "large_result_human.json")
PLOT_PATH   = os.path.join(BASE_DIR, "large_eval_human.png")

GROUPS = {
    "01": "advanced", "02": "advanced", "03": "advanced",
    "04": "advanced", "05": "advanced",
    "06": "intermediate", "07": "intermediate", "08": "intermediate",
    "09": "basic", "10": "basic",
}
GROUP_COLOR = {"advanced": "steelblue", "intermediate": "orange", "basic": "tomato"}

# Order in which speakers are listed in the plot (left to right)
SPEAKER_PLOT_ORDER = ["10", "09", "08", "06", "05", "03", "02", "04", "01"]

# ── Text normalization ────────────────────────────────────────────────────────

def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\säöüß]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

# ── Outlier removal (IQR-based) ───────────────────────────────────────────────

def drop_outliers(values):
    """Return values with extreme outliers (outside 1.5*IQR) removed"""
    if len(values) < 4:
        return values
    sorted_vals = sorted(values)
    n  = len(sorted_vals)
    q1 = sorted_vals[n // 4]
    q3 = sorted_vals[(3 * n) // 4]
    iqr = q3 - q1
    lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    return [v for v in values if lo <= v <= hi]

# ── Model loading ─────────────────────────────────────────────────────────────

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"[device] {device}")

processor = WhisperProcessor.from_pretrained(MODEL_ID, language=LANGUAGE, task=TASK)
# whisper-large-v3 ships fp16 weights; force float32 so they match the
# float32 input features from the processor (avoids "Half vs float" RuntimeError)
model     = WhisperForConditionalGeneration.from_pretrained(MODEL_ID, torch_dtype=torch.float32).to(device)
model.eval()
print(f"[model] {MODEL_ID} loaded")

# ── Inference & log-likelihood ────────────────────────────────────────────────

def transcribe(audio):
    inputs = processor(audio, sampling_rate=SAMPLE_RATE, return_tensors="pt").to(device)
    with torch.no_grad():
        pred_ids = model.generate(
            inputs.input_features, language=LANGUAGE, task=TASK,
        )
    return normalize(processor.batch_decode(pred_ids, skip_special_tokens=True)[0])

def log_likelihood(audio, ref_text):
    """Average per-token log-likelihood (higher = pronunciation closer to the reference)"""
    inputs    = processor(audio, sampling_rate=SAMPLE_RATE, return_tensors="pt").to(device)
    label_ids = processor.tokenizer(
        normalize(ref_text), return_tensors="pt"
    ).input_ids.to(device)
    with torch.no_grad():
        loss = model(input_features=inputs.input_features, labels=label_ids).loss
    return round(-loss.item(), 6)

# ── human: per-speaker / per-group evaluation (controlled identical sentences) ─

def shared_ylim(key, vals):
    """Read baseline/final/small/medium/large results together so all plots share
    the same y-axis range (lo, hi), with 0 included as a reference point"""
    all_vals = list(vals) + [0]
    for prefix in ("baseline", "final", "small", "medium", "large"):
        path = os.path.join(BASE_DIR, f"{prefix}_result_human.json")
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                other = json.load(f)
            all_vals += [s[key] for s in other.get("speakers", {}).values()
                         if s.get("num_samples", 0) > 0 and s.get(key) is not None]
    lo, hi = min(all_vals), max(all_vals)
    pad = (hi - lo) * 0.1 or 1.0
    return lo - pad, hi + pad

def run_human_eval():
    speaker_data = defaultdict(list)
    with open(LIST_CSV, encoding="utf-8-sig") as f:
        reader   = csv.DictReader(f)
        speakers = sorted(c for c in reader.fieldnames if c not in ("num", "KR", "DE"))
        for row in reader:
            num = int(row["num"])
            for speaker in speakers:
                raw   = row.get(speaker, "").strip()
                score = int(raw) if raw else None
                speaker_data[speaker].append((num, row["DE"], score))

    print(f"[data] human {len(speaker_data)} speakers: {list(speaker_data.keys())}")

    all_refs, all_hyps = [], []
    group_refs         = defaultdict(list)
    group_hyps         = defaultdict(list)
    speaker_results    = {}
    all_scores, all_ll, all_sample_wer = [], [], []

    for speaker, phrases in speaker_data.items():
        wav_dir = os.path.join(HUMAN_DIR, speaker, "wav")
        refs, hyps, records = [], [], []

        for num, german, score in phrases:
            fname    = f"{speaker}_{num}.wav"
            wav_path = os.path.join(wav_dir, fname)
            if not os.path.exists(wav_path):
                continue

            audio, _ = sf.read(wav_path, dtype="float32")
            ref = normalize(german)
            hyp = transcribe(audio)
            ll  = log_likelihood(audio, german)
            sample_wer = jiwer_wer([ref], [hyp])

            refs.append(ref)
            hyps.append(hyp)
            records.append({"id": num, "file": fname,
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

        print(f"[{speaker}({group})] WER={speaker_wer*100:.2f}%  LL={avg_ll:.4f}" if speaker_wer else f"[{speaker}] no files")

    overall_wer = jiwer_wer(all_refs, all_hyps) if all_refs else None
    group_wer   = {g: jiwer_wer(group_refs[g], group_hyps[g]) for g in group_refs if group_refs[g]}
    overall_ll  = round(sum(
        r["log_likelihood"] for s in speaker_results.values() for r in s["records"]
    ) / max(sum(s["num_samples"] for s in speaker_results.values()), 1), 6)

    print(f"\n[overall] WER={overall_wer*100:.2f}%  LL={overall_ll:.4f}")
    for g, w in group_wer.items():
        print(f"[{g}]  WER={w*100:.2f}%")

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
        print("\n[DA correlation] score not provided — skipping")

    result = {
        "timestamp": datetime.now().isoformat(), "model": MODEL_ID,
        "data": "human",
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

    speakers   = [s for s in SPEAKER_PLOT_ORDER
                  if s in speaker_results and speaker_results[s]["num_samples"] > 0]
    wer_vals   = [speaker_results[s]["wer_pct"] or 0 for s in speakers]
    ll_vals    = [speaker_results[s]["avg_log_likelihood"] or 0 for s in speakers]
    bar_colors = [GROUP_COLOR.get(GROUPS.get(s, ""), "gray") for s in speakers]

    n_plots = 4 if len(all_scores) >= 3 else 2
    fig, axes = plt.subplots(1, n_plots, figsize=(6 * n_plots, 5))
    if n_plots == 2:
        axes = list(axes)
    fig.suptitle("Whisper-large-v3 (original) · Human Speech Evaluation", fontsize=13)

    for ax, vals, ylabel, title, key in [
        (axes[0], wer_vals, "WER (%)",           "Word Error Rate",    "wer_pct"),
        (axes[1], ll_vals,  "Avg Log-Likelihood", "Log-Likelihood",     "avg_log_likelihood"),
    ]:
        bars = ax.bar(speakers, vals, color=bar_colors, edgecolor="white", width=0.6)
        ax.set_ylim(*shared_ylim(key, vals))
        for g, c in GROUP_COLOR.items():
            ax.bar(0, 0, color=c, label=f"{g} speakers")
        for bar, val in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + (max(vals) - min(vals)) * 0.02,
                    f"{val:.2f}", ha="center", va="bottom", fontsize=9)
        ax.set_xlabel("Speaker ID"); ax.set_ylabel(ylabel); ax.set_title(title)
        ax.legend(); ax.grid(axis="y", alpha=0.3)

    if len(all_scores) >= 3:
        r_ll, _  = spearmanr(all_scores, all_ll)
        r_wer, _ = spearmanr(all_scores, all_sample_wer)

        ll_by_score  = [[ll for s, ll in zip(all_scores, all_ll) if s == score] for score in (1, 2, 3)]
        wer_by_score = [drop_outliers([w * 100 for s, w in zip(all_scores, all_sample_wer) if s == score])
                        for score in (1, 2, 3)]

        ax = axes[2]
        ax.boxplot(ll_by_score, positions=[1, 2, 3], widths=0.5)
        ax.set_xlabel("DA Score"); ax.set_ylabel("Log-Likelihood")
        ax.set_title(f"Score vs LL  (ρ={r_ll:.3f})")
        ax.set_xticks([1, 2, 3]); ax.grid(alpha=0.3)

        ax = axes[3]
        ax.boxplot(wer_by_score, positions=[1, 2, 3], widths=0.5)
        ax.set_xlabel("DA Score"); ax.set_ylabel("WER (%)")
        ax.set_title(f"Score vs WER  (ρ={r_wer:.3f}, outliers excluded)")
        ax.set_xticks([1, 2, 3]); ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(PLOT_PATH, dpi=150)
    plt.close()
    print(f"[saved] {PLOT_PATH}")

# ── Run ───────────────────────────────────────────────────────────────────────

run_human_eval()
