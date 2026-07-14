"""
COMETKiwi-23-XL QE scoring

Output: src, ref, tgts, cometkiwi score, zscore, zQE, score gap
        + pearson r between zscore and mean cometkiwi across entries (dataset-level stat)

Requirements:
    pip install unbabel-comet scipy
"""

import json
import statistics
import torch
from pathlib import Path
from scipy.stats import pearsonr
from huggingface_hub import snapshot_download
from comet import load_from_checkpoint

# 입력 파일: WMT21 데이터셋 중 1,000개 샘플 (src, ref, tgts, zscore 포함)
INPUT_PATH = Path(__file__).parent / "wmt21_1k_dev.jsonl"
# 출력 파일: COMETKiwi 점수와 통계값을 추가한 결과 저장
OUTPUT_PATH = Path(__file__).parent / "wmt21_1k_cometkiwi.jsonl"

N_SAMPLES = 1000  # 처리할 최대 샘플 수
BATCH_SIZE = 16
MODEL_NAME = "Unbabel/wmt23-cometkiwi-da-xl"


def load_data(path: Path, n: int) -> list[dict]:
    """JSONL 파일에서 최대 N_SAMPLES개의 항목을 읽어 리스트로 반환."""
    data = []
    with open(path) as f:
        for i, line in enumerate(f):
            if i >= n:
                break
            data.append(json.loads(line))
    return data


def main():
    # ── 1. 데이터 로드 ────────────────────────────────────────────────────────
    data = load_data(INPUT_PATH, N_SAMPLES)
    print(f"Loaded {len(data)} samples from {INPUT_PATH.name}")

    # ── 2. 모델 로드 ──────────────────────────────────────────────────────────
    # snapshot_download: HuggingFace Hub에서 모델 전체를 로컬 캐시로 다운로드
    # load_from_checkpoint: COMET 라이브러리의 체크포인트 로더 (PyTorch Lightning 기반)
    model_path = snapshot_download(repo_id=MODEL_NAME)
    model = load_from_checkpoint(model_path + "/checkpoints/model.ckpt")

    # ── 3. (src, mt) 평탄화 ───────────────────────────────────────────────────
    # COMETKiwi는 참조 번역(ref) 없이 원문(src)과 기계 번역(mt)만으로 품질을 추정(QE)
    # 각 entry에는 여러 번역 후보(tgts)가 있으므로, 모든 쌍을 1차원 리스트로 펼침
    # index[(k)] = (i, j): flat_scores[k]가 data[i]의 j번째 번역 후보 점수임을 기록
    pairs = []
    index = []
    for i, entry in enumerate(data):
        src = entry["src"]
        for j, tgt in enumerate(entry["tgts"]):
            pairs.append({"src": src, "mt": tgt[0]})
            index.append((i, j))

    # ── 4. COMETKiwi 추론 ─────────────────────────────────────────────────────
    print(f"Scoring {len(pairs)} pairs with {MODEL_NAME} ...")
    gpus = 1 if torch.cuda.is_available() else 0
    # model.predict: 내부적으로 배치를 나눠 추론하고 output.scores에 float 리스트 반환
    output = model.predict(pairs, batch_size=BATCH_SIZE, gpus=gpus)
    flat_scores = output.scores  # len == len(pairs)

    # ── 5. 점수를 entry 단위로 재조립 ─────────────────────────────────────────
    # flat_scores는 전체 (src, mt) 쌍에 대한 1차원 점수 목록
    # index를 이용해 각 entry(문장)별로 번역 후보 점수 리스트를 복원
    cometkiwi_per_entry: list[list[float]] = [[] for _ in data]
    for (i, _j), score in zip(index, flat_scores):
        cometkiwi_per_entry[i].append(score)

    # ── 6. 데이터셋 수준 통계: Pearson r ──────────────────────────────────────
    # zscore: WMT21 전체 기준으로 정규화된 값이므로 이 1k 샘플 내에서 재정규화
    # → zscore와 zQE를 동일 척도(이 샘플 기준 mean=0, std=1)로 맞춰야 score_gap 비교가 유효
    raw_zscores = [entry["zscore"] for entry in data]
    zs_mean = statistics.mean(raw_zscores)
    zs_std = statistics.stdev(raw_zscores)
    zscores = [(v - zs_mean) / zs_std for v in raw_zscores]

    qe_means = [sum(scores) / len(scores) for scores in cometkiwi_per_entry]
    r, _ = pearsonr(zscores, qe_means)
    print(f"Pearson r (zscore vs cometkiwi): {r:.4f}")

    # ── 7. COMETKiwi 점수 Z-정규화 (zQE) ─────────────────────────────────────
    # zQE = (qe_mean_i - μ) / σ  (이 샘플 기준, zscore와 동일 척도)
    qe_mean = statistics.mean(qe_means)
    qe_std = statistics.stdev(qe_means)
    qe_z = [(v - qe_mean) / qe_std for v in qe_means]

    # ── 8. 결과 저장 ──────────────────────────────────────────────────────────
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        for entry, scores, cz, zs in zip(data, cometkiwi_per_entry, qe_z, zscores):
            out = {
                "src": entry["src"],
                "ref": entry["ref"],
                "tgts": [tgt[0] for tgt in entry["tgts"]],
                "cometkiwi": scores,  # 각 번역 후보의 원시 COMETKiwi 점수 목록
                "zscore": round(zs, 6),  # 인간 평가 Z-점수 (이 샘플 내 재정규화)
                "zQE": round(cz, 6),  # COMETKiwi 평균의 Z-정규화 값
                "score_gap": round(
                    zs - cz, 6
                ),  # 인간 평가와 자동 지표 간의 차이 (동일 척도 비교)
            }
            f.write(json.dumps(out, ensure_ascii=False) + "\n")

    print(f"Saved → {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
