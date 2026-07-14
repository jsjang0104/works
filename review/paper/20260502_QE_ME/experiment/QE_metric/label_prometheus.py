"""
Prometheus-2 (7B) QE scoring
Uses transformers directly (vllm 의존성 문제가 나타나서 사용x).

Output: src, ref, tgts, prometheus score (raw 1-5), feedback, zscore, zQE, score gap
        + pearson r between zscore and mean prometheus across entries (dataset-level stat)

Requirements:
    pip install transformers scipy accelerate
"""

import json
import re
import statistics
import torch
from pathlib import Path
from scipy.stats import pearsonr
from transformers import AutoModelForCausalLM, AutoTokenizer

# 입력 파일: WMT21 데이터셋 중 1,000개 샘플 (src, ref, tgts, zscore 포함)
INPUT_PATH = Path(__file__).parent / "wmt21_1k_dev.jsonl"
# 출력 파일: Prometheus 점수·피드백과 통계값을 추가한 결과 저장
OUTPUT_PATH = Path(__file__).parent / "wmt21_1k_prometheus.jsonl"

N_SAMPLES = 1000  # 처리할 최대 샘플 수
BATCH_SIZE = 4
MODEL_NAME = "prometheus-eval/prometheus-7b-v2.0"  # HuggingFace Hub 모델 ID
MAX_NEW_TOKENS = 512  # 피드백 + "[RESULT] N" 형식으로 생성할 최대 토큰 수

# Prometheus-2 절대 평가(absolute grading) 프롬프트 템플릿
# 논문 템플릿 그대로 사용 (https://arxiv.org/pdf/2310.08491 Appendix H)

PROMPT_TEMPLATE = """\
###Task Description:
An instruction (might include an Input inside it), a response to evaluate, \
and a score rubric representing a evaluation criteria are given.
1. Write a detailed feedback that assess the quality of the response strictly \
based on the given score rubric, not evaluating in general.
2. After writing a feedback, write a score that is an integer between 1 and 5. \
You should refer to the score rubric.
3. The output format should look as follows: \
"(write a feedback for criteria) [RESULT] (an integer number between 1 and 5)"
4. Please do not generate any other opening, closing, and explanations.

###The instruction to evaluate:
{instruction}

###Response to evaluate:
{response}

###Score Rubrics:
[Translation quality from English to German]
Score 1: The translation is incomprehensible or completely wrong. Critical meaning is lost or entirely distorted.
Score 2: The translation has major errors that significantly distort the meaning. It is difficult to understand the intended message.
Score 3: The translation conveys the general meaning but contains noticeable errors in grammar, word choice, or fluency that affect readability.
Score 4: The translation is accurate and mostly fluent with only minor errors that do not affect the overall understanding.
Score 5: The translation is perfectly accurate and natural. It reads as if written by a native speaker with no errors.

###Feedback: """


def load_data(path: Path, n: int) -> list[dict]:
    """JSONL 파일에서 최대 n개의 항목을 읽어 리스트로 반환."""
    data = []
    with open(path) as f:
        for i, line in enumerate(f):
            if i >= n:
                break
            data.append(json.loads(line))
    return data


def build_prompt(src: str, hyp: str) -> str:
    """원문(src)과 번역 가설(hyp)을 PROMPT_TEMPLATE에 삽입해 완성된 프롬프트를 반환."""
    instruction = (
        f"Evaluate the quality of the following machine translation "
        f"from English to German.\n\nEnglish source: {src}"
    )
    return PROMPT_TEMPLATE.format(instruction=instruction, response=hyp)


def parse_score(text: str) -> int | None:
    """
    모델 출력 텍스트에서 1~5 정수 점수를 추출.

    우선 논문 형식인 '[RESULT] N' 패턴을 찾고,
    없으면 마지막 단독 숫자(1~5)를 fallback으로 사용.
    파싱 자체가 실패하면 None 반환 (호출부에서 기본값 3으로 처리).
    """
    match = re.search(r"\[RESULT\]\s*([1-5])", text)
    if match:
        return int(match.group(1))
    # Fallback: 독립된 1~5 숫자 중 마지막 것을 점수로 간주
    digits = re.findall(r"\b([1-5])\b", text)
    return int(digits[-1]) if digits else None


def batch_score(
    prompts: list[str],
    tokenizer: AutoTokenizer,
    model: AutoModelForCausalLM,
    device: torch.device,
    batch_size: int,
) -> list[tuple[int | None, str]]:
    """
    프롬프트 리스트를 배치 단위로 모델에 입력하고 (점수, 피드백) 튜플 목록을 반환.

    반환값: [(score_or_None, feedback_text), ...]  (len == len(prompts))
    """
    results = []
    for i in range(0, len(prompts), batch_size):
        batch = prompts[i : i + batch_size]

        # 배치 내 프롬프트를 토크나이즈 (길이 맞춤을 위해 패딩 적용)
        # truncation=True: max_length(2048) 초과 시 앞부분 잘라냄
        inputs = tokenizer(
            batch,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=2048,
        ).to(device)

        with torch.no_grad():
            # do_sample=False: greedy decoding → 결정론적 출력 (재현성 보장)
            # pad_token_id=eos_token_id: LLaMA 계열은 패드 토큰이 없으므로 EOS로 대체
            outputs = model.generate(
                **inputs,
                max_new_tokens=MAX_NEW_TOKENS,
                do_sample=False,
                pad_token_id=tokenizer.eos_token_id,
            )

        for j, seq in enumerate(outputs):
            # outputs에는 입력 토큰이 그대로 포함되어 있으므로,
            # 입력 길이(input_len) 이후의 토큰만 잘라내어 새로 생성된 텍스트만 디코딩
            input_len = inputs["input_ids"].shape[1]
            new_tokens = seq[input_len:]
            decoded = tokenizer.decode(new_tokens, skip_special_tokens=True)
            results.append((parse_score(decoded), decoded.strip()))

        print(f"  {min(i + batch_size, len(prompts))}/{len(prompts)} pairs scored")

    return results


def main():
    # ── 1. 데이터 로드 ────────────────────────────────────────────────────────
    data = load_data(INPUT_PATH, N_SAMPLES)
    print(f"Loaded {len(data)} samples from {INPUT_PATH.name}")

    # ── 2. 디바이스 및 모델 설정 ──────────────────────────────────────────────
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    print(f"Loading {MODEL_NAME} ...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    # causal LM 배치 추론 시 오른쪽 패딩 대신 왼쪽 패딩을 사용해야
    # 배치 내 각 시퀀스의 마지막 실제 토큰이 동일한 위치에서 생성을 시작할 수 있음
    tokenizer.padding_side = "left"
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.bfloat16,  # 메모리 절약 (fp32 대비 절반), 정밀도 손실 미미
        device_map="auto",  # 가용 GPU/CPU에 레이어를 자동 분산 배치
    )
    model.eval()  # dropout 등 학습 전용 동작 비활성화

    # ── 3. 프롬프트 생성 및 인덱스 매핑 ──────────────────────────────────────
    # 각 entry의 번역 후보(tgts)를 평탄화하여 1차원 프롬프트 목록 생성
    # index[(k)] = (i, j): flat_results[k]가 data[i]의 j번째 번역 후보임을 기록
    prompts, index = [], []
    for i, entry in enumerate(data):
        for j, tgt in enumerate(entry["tgts"]):
            prompts.append(build_prompt(entry["src"], tgt[0]))
            index.append((i, j))

    # ── 4. Prometheus 추론 ────────────────────────────────────────────────────
    print(f"Scoring {len(prompts)} pairs with {MODEL_NAME} ...")
    flat_results = batch_score(prompts, tokenizer, model, device, BATCH_SIZE)

    # ── 5. 결과를 entry 단위로 재조립 ─────────────────────────────────────────
    # parse_score가 None을 반환한 경우(파싱 실패) 중립값 3으로 대체
    prometheus_per_entry: list[list[int]] = [[] for _ in data]
    feedback_per_entry: list[list[str]] = [[] for _ in data]
    for (i, _j), (score, feedback) in zip(index, flat_results):
        prometheus_per_entry[i].append(score if score is not None else 3)
        feedback_per_entry[i].append(feedback)

    # ── 6. 데이터셋 수준 통계: Pearson r ──────────────────────────────────────
    # zscore: WMT21 전체 기준으로 정규화된 값이므로 이 1k 샘플 내에서 재정규화
    # → zscore와 zQE를 동일 척도(이 샘플 기준 mean=0, std=1)로 맞춰야 score_gap 비교가 유효
    raw_zscores = [entry["zscore"] for entry in data]
    zs_mean = statistics.mean(raw_zscores)
    zs_std = statistics.stdev(raw_zscores)
    zscores = [(v - zs_mean) / zs_std for v in raw_zscores]

    qe_means = [sum(scores) / len(scores) for scores in prometheus_per_entry]
    r, _ = pearsonr(zscores, qe_means)
    print(f"Pearson r (zscore vs prometheus): {r:.4f}")

    # ── 7. Prometheus 점수 Z-정규화 (zQE) ────────────────────────────────────
    # zQE = (qe_mean_i - μ) / σ  (이 샘플 기준, zscore와 동일 척도)
    qe_mean = statistics.mean(qe_means)
    qe_std = statistics.stdev(qe_means)
    qe_z = [(v - qe_mean) / qe_std for v in qe_means]

    # ── 8. 결과 저장 ──────────────────────────────────────────────────────────
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        for entry, scores, feedbacks, cz, zs in zip(
            data, prometheus_per_entry, feedback_per_entry, qe_z, zscores
        ):
            out = {
                "src": entry["src"],
                "ref": entry["ref"],
                "tgts": [tgt[0] for tgt in entry["tgts"]],
                "prometheus": scores,  # 각 번역 후보의 원시 1~5 점수 목록
                "feedback": feedbacks,  # 각 번역 후보에 대한 Prometheus 피드백 텍스트
                "zscore": round(zs, 6),  # 인간 평가 Z-점수 (이 샘플 내 재정규화)
                "zQE": round(cz, 6),  # Prometheus 평균의 Z-정규화 값
                "score_gap": round(
                    zs - cz, 6
                ),  # 인간 평가와 자동 지표 간의 차이 (동일 척도 비교)
            }
            f.write(json.dumps(out, ensure_ascii=False) + "\n")

    print(f"Saved → {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
