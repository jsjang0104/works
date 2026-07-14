"""
LLM-as-a-Judge score generation — vLLM + Llama version (전체 데이터셋).

vLLM을 이용해 Llama 3.1 8B-Instruct를 로컬에서 돌려 전체 데이터셋을 평가.
API key 불필요, rate limit 없음.

Generates 2 CSV files expected by 01-eval_all.py:
llama-3.1-8b-instruct_{source,target}_based_num_scores.csv
"""

import re
import sys
import math
from pathlib import Path

import pandas as pd
from vllm import LLM, SamplingParams

# ── path setup ─────────────────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# ── config ─────────────────────────────────────────────────────────────────────
MODEL_NAME = "meta-llama/Llama-3.1-8B-Instruct"
MODEL_DIR = "llama"
MODEL_SUFFIX = "llama-3.1-8b-instruct"
PROTOCOL = "esa"

# Langauge Pair Set
LPS = ["en-cs", "en-es", "en-hi", "en-is", "en-ja", "en-ru", "en-uk", "en-zh"]

LANGUAGE_MAPPING = {
    "cs": "Czech",
    "es": "Spanish",
    "hi": "Hindi",
    "is": "Icelandic",
    "ja": "Japanese",
    "ru": "Russian",
    "uk": "Ukrainian",
    "zh": "Chinese",
}

OUTPUT_BASE = (
    Path(__file__).resolve().parent.parent.parent / "data" / "LLM-as-a-Judge" / PROTOCOL
)

# ── prompts (원본 llm_as_a_judge/main.py에서 가져옴) ─────────────────────────────
TEMPLATE_SOURCE = (
    "You are given a source text. Your goal is to determine the approximate proficiency level required to translate this text, based on a detailed analysis of its complexity. The final result should be reported as a single numeric score on a scale of 0 to 120, where higher numbers correspond to a higher difficulty (i.e., more advanced language proficiency requirements). You should also relate this numeric score to commonly recognized proficiency levels (e.g., A1, A2, B1, B2, C1, C2). Here is the expected mapping: 0-20 for A1 (Beginner); 21-40 for A2 (Elementary); 41-60 for B1 (Intermediate); 61-80 for B2 (Upper Intermediate); 81-100 for C1 (Advanced); 101-120 for C2 (Mastery)."
    "Instructions: First, examine the text to identify features that affect reading difficulty, including complexity of vocabulary, grammar, semantic density, and any specialized knowledge required. Then, provide a brief explanation of your reasoning for each major factor. Consider whether the text includes domain-specific terminology, cultural references, idiomatic expressions, or advanced grammatical constructions. Finally, assign a numeric score from 0 to 120 and map that score to one of the CEFR levels. Conclude with a final statement that clearly states your numeric score and the corresponding proficiency level surrounded by triple square brackets, for example [[[86, C1 (Advanced)]]]"
    "Analyze following text:\n{src}"
)

TEMPLATE_TARGET = (
    "You are given a source text. Your goal is to determine the approximate proficiency level required to translate this text into {target_language}, based on a detailed analysis of its complexity. The final result should be reported as a single numeric score on a scale of 0 to 120, where higher numbers correspond to a higher difficulty (i.e., more advanced language proficiency requirements). You should also relate this numeric score to commonly recognized proficiency levels (e.g., A1, A2, B1, B2, C1, C2). Here is the expected mapping: 0-20 for A1 (Beginner); 21-40 for A2 (Elementary); 41-60 for B1 (Intermediate); 61-80 for B2 (Upper Intermediate); 81-100 for C1 (Advanced); 101-120 for C2 (Mastery)."
    "Instructions: First, examine the text to identify features affecting the translation into {target_language}, which affect reading difficulty, including complexity of vocabulary, grammar, semantic density, and any specialized knowledge required. Then, provide a brief explanation of your reasoning for each major factor. Consider whether the text includes domain-specific terminology, cultural references, idiomatic expressions, or advanced grammatical constructions. Finally, assign a numeric score from 0 to 120 and map that score to one of the CEFR levels. Conclude with a final statement that clearly states your numeric score and the corresponding proficiency level surrounded by triple square brackets, for example [[[86, C1 (Advanced)]]]."
    "Analyze following text:\n{src}"
)


# ── score parsing ──────────────────────────────────────────────────────────────


def parse_score(text: str) -> float:
    """
    Extract numeric score from LLM output.

    파싱 우선순위:
    1. [[[N, CEFR]]] — 콤마 뒤 문자열은 무시, 숫자만 추출
    2. "overall" / "final" / "total" / "score" 키워드 근처 숫자
    3. 마지막으로 등장하는 20 이상의 독립 숫자 (소분석 점수 제외)
    4. 모두 실패 시 NaN
    결과는 0-120 범위로 클램핑.
    """
    if text is None or (isinstance(text, float) and math.isnan(text)):
        return math.nan

    text = str(text)

    # 1순위: [[[N, CEFR text]]] 형식
    m = re.search(r"\[\[\[\s*(\d+(?:\.\d+)?)\s*(?:,|\]\]\])", text)
    if m:
        return min(float(m.group(1)), 120.0)

    # 2순위: "overall" / "final score" / "total score" 근처의 숫자
    keyword_patterns = [
        r"(?:overall|final|total)(?:[^\d]{0,40}?)(\d{2,3})",
        r"(?:score|estimate|rating)(?:[^\d]{0,30}?)(\d{2,3})",
        r"(\d{2,3})(?:\s*(?:out of|/|on a scale))",
    ]
    for pattern in keyword_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            val = float(matches[-1])
            if 10 <= val <= 120:
                return float(val)

    # 3순위: 20 이상의 마지막 독립 숫자 (소분석 점수 "10", "5" 등 제외)
    nums = re.findall(r"\b(\d{2,3})\b", text)
    large_nums = [float(n) for n in nums if float(n) >= 20]
    if large_nums:
        return min(large_nums[-1], 120.0)

    # 4순위: 아무 숫자라도 있으면 마지막 것
    all_nums = re.findall(r"\b(\d{1,3})\b", text)
    if all_nums:
        return min(float(all_nums[-1]), 120.0)

    return math.nan


# ── core scoring (vLLM 배치 추론) ──────────────────────────────────────────────


def score_texts(
    llm: LLM,
    sampling_params: SamplingParams,
    texts: list[str],
    template: str,
    template_kwargs: list[dict],
) -> tuple[list[float], list[str]]:
    """
    vLLM 배치 추론으로 전체 texts를 한꺼번에 평가.
    chat 템플릿을 적용해 Llama Instruct 형식에 맞춰 생성.
    Returns: (scores, raw_outputs)
    """
    # 프롬프트 생성 → chat 형식 변환
    conversations = []
    for src, kwargs in zip(texts, template_kwargs):
        prompt = template.format(src=src, **kwargs)
        conversations.append([{"role": "user", "content": prompt}])

    print(f"    Batch inference: {len(conversations)} prompts ...")
    outputs = llm.chat(conversations, sampling_params)

    # 점수 파싱
    scores = []
    raw_outputs = []
    for i, output in enumerate(outputs):
        raw = output.outputs[0].text
        raw_outputs.append(raw)
        score = parse_score(raw)
        scores.append(score)
        # 처음 3개 + 매 500개마다 로그 출력
        if i < 3 or i % 500 == 0:
            print(
                f"    [{i+1}/{len(texts)}] score={score:.0f}  raw='{raw[:80].strip()}'"
            )

    valid = sum(1 for s in scores if not math.isnan(s))
    print(f"    → {valid}/{len(scores)} valid scores")
    return scores, raw_outputs


# ── CSV generation ─────────────────────────────────────────────────────────────


def generate_csv(
    data,
    llm: LLM,
    sampling_params: SamplingParams,
    mode: str,  # "source" | "target"
):
    """
    Generate one source_based or target_based CSV file.

    CSV format: `lp` column (one row per source item per LP).
    apply_llm_as_a_judge() handles both `src_lang` and `lp` column styles;
    we use `lp` here so each LP gets its own correctly-sized list.
    """
    template = TEMPLATE_SOURCE if mode == "source" else TEMPLATE_TARGET
    out_dir = OUTPUT_BASE / MODEL_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{MODEL_SUFFIX}_{mode}_based_num_scores.csv"

    all_rows: list[dict] = []

    for lp in LPS:
        if lp not in data.lp2src_data_list:
            print(f"  [skip] {lp} not in data")
            continue
        src_data = data.lp2src_data_list[lp]
        tgt_lang = LANGUAGE_MAPPING[lp.split("-")[1]]

        texts = [item["src"] for item in src_data]
        kwargs = (
            [{"target_language": tgt_lang}] * len(texts)
            if mode == "target"
            else [{} for _ in texts]
        )

        print(f"\n  LP={lp}  mode={mode}  ({len(texts)} sentences, scoring ALL)")
        scores, raw_outputs = score_texts(llm, sampling_params, texts, template, kwargs)

        for i, (score, raw) in enumerate(zip(scores, raw_outputs)):
            item = src_data[i]
            human_scores = [
                item["scores"][sys_name]["human"] for sys_name in item["scores"]
            ]
            avg_esa = sum(human_scores) / len(human_scores) if human_scores else None
            all_rows.append(
                {
                    "lp": lp,
                    "src": item["src"],
                    "avg_human_esa": avg_esa,
                    "numeric_score": score if not math.isnan(score) else None,
                    "raw_output": raw,
                }
            )

    df = pd.DataFrame(all_rows)
    df.to_csv(out_path, index=False)
    n_real = df["numeric_score"].notna().sum()
    print(f"\n  → Saved: {out_path}  ({n_real} real scores, {len(df)-n_real} NaN)")
    return out_path


# ── main ───────────────────────────────────────────────────────────────────────


def main():
    import difficulty_estimation.data

    # ── vLLM 모델 로드 (한 번만) ──────────────────────────────────────────────
    print(f"Loading vLLM model: {MODEL_NAME} ...")
    llm = LLM(
        model=MODEL_NAME,
        tensor_parallel_size=1,
        gpu_memory_utilization=0.9,
        max_model_len=4096,  # 이 태스크는 긴 컨텍스트 불필요
    )
    sampling_params = SamplingParams(
        max_tokens=1024,  # Llama는 분석을 길게 쓰므로 [[[N]]]까지 도달하게 충분한 토큰 필요
        temperature=0.0,
    )

    # ── 데이터 로드 ──────────────────────────────────────────────────────────
    print("Loading WMT24 data...")
    data = difficulty_estimation.data.Data.load(
        dataset_name="wmt24", lps=["all"], domains="all", protocol=PROTOCOL
    )

    # ── source-based, target-based 순서로 평가 ────────────────────────────────
    for mode in ["source", "target"]:
        print(f"\n{'='*60}")
        print(f"  Model: {MODEL_SUFFIX}  Mode: {mode}")
        print(f"{'='*60}")
        generate_csv(data, llm, sampling_params, mode)

    print("\nAll done! Now you can run: python 01-eval_all.py")


if __name__ == "__main__":
    main()
