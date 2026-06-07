"""
파인튜닝된 Whisper-tiny로 음성 인식 평가

데이터 선택(--data):
  human : data/human/{speaker}/wav/ + data/human/recording_list.csv
          실제 환경 음성 + 발음 수준(advanced/intermediate/basic) 그룹 비교용
          (모든 화자가 동일한 25문장을 녹음 — 내용을 통제하고 화자·발음 차이를 비교)
  tts   : data/tts/test/wav/ + data/tts/test/transcripts.csv
          서로 다른 다수의 문장에 대한 일반 인식력 확인용 (gTTS 합성 음성, 대량)

출력:   asr/eval/final_result_{human|tts}.json
        asr/eval/final_eval_{human|tts}.png

화자 그룹 (human)
  advanced     : hw_ha, jk_hong, mk_cho, mc_park, jw_kim
  intermediate : js_jang, kj_lee, ts_ham
  basic        : jw_choi

human 모드에서 score 열이 채워진 경우 DA score vs WER / LL Spearman 상관관계를 추가로 계산합니다.

사용법:
    python final_evaluate.py --data human
    python final_evaluate.py --data tts
"""

import argparse
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

# ── 인자 ──────────────────────────────────────────────────────────────────────

parser = argparse.ArgumentParser(
    description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
)
parser.add_argument(
    "--data", choices=["human", "tts"], default="human",
    help="평가 데이터셋: human(실제 환경·발음 수준 그룹 비교) 또는 tts(다양한 문장 인식력)",
)
args = parser.parse_args()

# ── 설정 ──────────────────────────────────────────────────────────────────────

LANGUAGE    = "german"
TASK        = "transcribe"
SAMPLE_RATE = 16000

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
DATA_DIR    = os.path.join(BASE_DIR, "..", "..", "data")
MODEL_DIR   = os.path.join(BASE_DIR, "..", "whisper-tiny-german")

HUMAN_DIR   = os.path.join(DATA_DIR, "human")
LIST_CSV    = os.path.join(HUMAN_DIR, "recording_list.csv")

TTS_DIR     = os.path.join(DATA_DIR, "tts", "test")
TTS_CSV     = os.path.join(TTS_DIR, "transcripts.csv")

RESULT_PATH = os.path.join(BASE_DIR, f"final_result_{args.data}.json")
PLOT_PATH   = os.path.join(BASE_DIR, f"final_eval_{args.data}.png")

GROUPS = {
    "hw_ha":   "advanced", "jk_hong": "advanced",
    "mk_cho":  "advanced", "mc_park": "advanced",
    "jw_kim":  "advanced",
    "js_jang": "intermediate", "kj_lee": "intermediate", "ts_ham": "intermediate",
    "jw_choi": "basic",
}
GROUP_COLOR = {"advanced": "steelblue", "intermediate": "orange", "basic": "tomato"}

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

# ── human: 화자별 / 발음 그룹별 평가 (통제된 동일 문장) ────────────────────────

def run_human_eval():
    speaker_data = defaultdict(list)
    with open(LIST_CSV, encoding="utf-8") as f:
        reader   = csv.DictReader(f)
        speakers = [c for c in reader.fieldnames if c not in ("num", "KR", "DE")]
        for row in reader:
            num = int(row["num"])
            for speaker in speakers:
                raw   = row.get(speaker, "").strip()
                score = int(raw) if raw else None
                speaker_data[speaker].append((num, row["KR"], row["DE"], score))

    print(f"[data] human {len(speaker_data)}명: {list(speaker_data.keys())}")

    all_refs, all_hyps = [], []
    group_refs         = defaultdict(list)
    group_hyps         = defaultdict(list)
    speaker_results    = {}
    all_scores, all_ll, all_sample_wer = [], [], []

    for speaker, phrases in speaker_data.items():
        wav_dir = os.path.join(HUMAN_DIR, speaker, "wav")
        refs, hyps, records = [], [], []

        for num, korean, german, score in phrases:
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
            records.append({"id": num, "file": fname, "KR": korean,
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

    result = {
        "timestamp": datetime.now().isoformat(), "model": os.path.abspath(MODEL_DIR),
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

# ── tts: 다양한 문장에 대한 일반 인식력 평가 (대량 무작위 합성 음성) ───────────

def run_tts_eval():
    wav_dir = os.path.join(TTS_DIR, "wav")
    with open(TTS_CSV, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    print(f"[data] tts test {len(rows)}개 문장")

    refs, hyps, records = [], [], []
    for row in rows:
        wav_path = os.path.join(wav_dir, row["filename"])
        if not os.path.exists(wav_path):
            continue

        audio, _ = sf.read(wav_path, dtype="float32")
        ref = normalize(row["transcript"])
        hyp = transcribe(audio)
        ll  = log_likelihood(audio, row["transcript"])
        sample_wer = jiwer_wer([ref], [hyp])

        refs.append(ref)
        hyps.append(hyp)
        records.append({"id": len(records), "file": row["filename"], "korean": row["korean"],
                        "ref": ref, "hyp": hyp,
                        "log_likelihood": ll, "sample_wer": round(sample_wer, 4)})

    overall_wer = jiwer_wer(refs, hyps) if refs else None
    overall_ll  = round(sum(r["log_likelihood"] for r in records) / len(records), 6) if records else None

    print(f"\n[overall] WER={overall_wer*100:.2f}%  LL={overall_ll:.4f}  (n={len(records)})")

    result = {
        "timestamp": datetime.now().isoformat(), "model": os.path.abspath(MODEL_DIR),
        "data": "tts_test", "num_samples": len(records),
        "overall_wer": round(overall_wer, 6) if overall_wer else None,
        "overall_wer_pct": round(overall_wer * 100, 2) if overall_wer else None,
        "overall_log_likelihood": overall_ll,
        "records": records,
    }
    with open(RESULT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n[saved] {RESULT_PATH}")

    sample_wers = [r["sample_wer"] * 100 for r in records]
    sample_lls  = [r["log_likelihood"] for r in records]

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle("Whisper-tiny (fine-tuned) · TTS Test Set (다양한 문장 인식력)", fontsize=13)

    axes[0].hist(sample_wers, bins=20, color="steelblue", edgecolor="white")
    axes[0].axvline(overall_wer * 100, color="tomato", linestyle="--", label=f"overall={overall_wer*100:.2f}%")
    axes[0].set_xlabel("Sample WER (%)"); axes[0].set_ylabel("Count")
    axes[0].set_title("Per-sample WER distribution"); axes[0].legend(); axes[0].grid(alpha=0.3)

    axes[1].hist(sample_lls, bins=20, color="steelblue", edgecolor="white")
    axes[1].axvline(overall_ll, color="tomato", linestyle="--", label=f"avg={overall_ll:.4f}")
    axes[1].set_xlabel("Log-Likelihood"); axes[1].set_ylabel("Count")
    axes[1].set_title("Per-sample log-likelihood distribution"); axes[1].legend(); axes[1].grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(PLOT_PATH, dpi=150)
    plt.close()
    print(f"[saved] {PLOT_PATH}")

# ── 실행 ──────────────────────────────────────────────────────────────────────

if args.data == "human":
    run_human_eval()
else:
    run_tts_eval()
