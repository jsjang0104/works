"""
1. 대상 번역물 선택:
   - `llms`: WMT24 공식 LLM 4종류 (Claude-3.5, GPT-4, Tower-70B, IKUN-C)
   - `ref`: WMT24 공식 정답 텍스트 (refA)
   - `true`: WMT24에 존재는 모든 시스템의 번역물을 취합하여 평균 산출 (True Crowd)
2. 메트릭 선택:
    - `XCOMET-XXL`
    - `MetricX-XXL`

사용 예시:
    # Artificial Crowd (LLMs)
    python eval_crowd-based_dec.py --metric MetricX-XXL --target_type llms
    # True Crowd (All Systems)
    python eval_crowd-based_dec.py --metric MetricX-XXL --target_type true
    # Global Reference (refA)
    python eval_crowd-based_dec.py --metric MetricX-XXL --target_type ref
"""

import sys
import os
import torch
import logging
import argparse
import collections
import scipy.stats
import numpy as np
from pathlib import Path
from collections import defaultdict
from tqdm import tqdm
from typing import List, Optional, Dict, Set, Literal

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))
from difficulty_estimation.data import Data

# 실행 과정 터미널 출력
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# config
XCOMET_MODEL_NAME = "Unbabel/XCOMET-XXL"  # 논문 그대로 구현
METRICX_MODEL_NAME = "google/metricx-24-hybrid-xxl-v2p6"  # 논문 그대로 구현
WMT24_LLMS = ["Claude-3.5", "GPT-4", "Unbabel-Tower70B", "IKUN-C"]  # 직접 고름
WMT24_REF = ["refA"]  # 논문에 명시되어 있지 않았던 옵션
PROTOCOL = "esa"  # 논문 그대로 구현
BATCH_SIZE = 1

# =====================================================================
# evaluate에 필요 함수들 (기존 코드에 구현되어 있던 내용을 가져옴으로서 외부 라이브러리 의존성을 최소화)
# =====================================================================

MainResult = collections.namedtuple(
    "MainResult", ["avg_score", "avg_perfect", "diff_tau", "diff_pearson"]
)


def get_src_score_local(
    src_data: dict, scorer_name: str, systems_to_filter: Optional[List[str]] = None
) -> float:
    """특정 소스 문장에 대해 특정 메트릭(또는 인간)의 점수를 추출"""
    scores = src_data["scores"]
    # 인간 점수일 경우: 해당 소스에 대한 모든 시스템의 인간 점수를 평균
    if scorer_name == "human":
        sum_val, n = 0, 0
        for sys in scores:
            if systems_to_filter is None or sys not in systems_to_filter:
                sum_val += scores[sys]["human"]
                n += 1
        return sum_val / n if n > 0 else 0.0
    # LLM 점수일 경우: 첫번째 반환되는 LLM의 점수를 사용
    return scores[next(iter(scores))][scorer_name]


def get_round_robin_sorted_src_data_ids_local(
    lp2src_data_list: Dict[str, List[dict]], method_name: str
) -> List[int]:
    """여러 언어쌍에 걸쳐 균등하게 서브셋을 뽑기 위한 라운드-로빈 정렬 ID를 생성합"""
    lp2sorted_ids = {
        lp: [
            idx
            for idx, src_data in sorted(
                enumerate(src_list),
                key=lambda p: get_src_score_local(p[1], method_name),
            )
        ]
        for lp, src_list in lp2src_data_list.items()
    }
    sorted_ids, seen = [], set()
    while len(sorted_ids) < len(next(iter(lp2src_data_list.values()))):
        for lp_ids in lp2sorted_ids.values():
            if not lp_ids:
                continue
            cid = lp_ids.pop(0)
            if cid not in seen:
                seen.add(cid)
                sorted_ids.append(cid)
    return sorted_ids


def main_eval_local(
    src_data_list: List[dict],
    method_name: str,
    budget: int = 100,
    protocol: str = "esa",
    sorted_ids: Optional[List[int]] = None,
):
    """단일 언어쌍에 대해 DEC 계산"""
    # 1. 난이도 점수(QE 점수) 기준으로 하위 25% (어려운 문장들) 서브셋 추출
    if sorted_ids is None:
        avg_scores = [
            np.average([s[method_name] for s in d["scores"].values()])
            for d in src_data_list
        ]
        src_data_budget = [
            d for d, s in sorted(zip(src_data_list, avg_scores), key=lambda x: x[1])
        ][:budget]
    else:
        src_data_budget = [src_data_list[idx] for idx in sorted_ids[:budget]]

    # 2. 서브셋의 평균 인간 품질 점수 계산
    avg_human = np.average(
        [
            line["scores"][sys]["human"]
            for line in src_data_budget
            for sys in line["scores"]
        ]
    )
    avg_perfect = np.average(
        [
            line["scores"][sys]["human"] == (100 if protocol == "esa" else 0)
            for line in src_data_budget
            for sys in line["scores"]
        ]
    )
    # 3. DEC 핵심: 난이도 추정치(QE)와 실제 인간 점수(Human) 사이의 켄달타우 상관계수 산출
    taus = []
    all_sys = set([sys for d in src_data_list for sys in d["scores"]])
    for sys in all_sys:
        m_vals, h_vals = [], []
        is_llm = "LLM-as-a-Judge" in method_name
        for d in src_data_list:
            if sys in d["scores"]:
                m, h = d["scores"][sys][method_name], d["scores"][sys]["human"]
                if is_llm and abs(m - (-60.0)) < 1e-6:
                    continue
                m_vals.append(m)
                h_vals.append(h)
        if len(m_vals) > 1:
            res = scipy.stats.kendalltau(
                m_vals, h_vals, variant="b", nan_policy="omit"
            ).statistic
            if not np.isnan(res):
                taus.append(res)

    return MainResult(
        avg_score=avg_human,
        avg_perfect=avg_perfect,
        diff_tau=np.average(taus) if taus else None,
        diff_pearson=None,
    )


def main_eval_avg_local(
    method_name: str,
    data: Data,
    single_src_subset: bool = False,
    is_method_tgt_lang_dep: bool = False,
    budget: int = None,
    proportion: float = None,
):
    """모든 언어쌍의 결과를 종합하여 최종 Macro-Average DEC를 반환"""
    lp2src = data.lp2src_data_list
    results = []
    if single_src_subset and is_method_tgt_lang_dep:
        sids = get_round_robin_sorted_src_data_ids_local(lp2src, method_name)
        for slist in lp2src.values():
            results.append(
                main_eval_local(
                    slist,
                    method_name,
                    budget or int(len(slist) * proportion),
                    PROTOCOL,
                    sids,
                )
            )
    else:
        for slist in lp2src.values():
            results.append(
                main_eval_local(
                    slist, method_name, budget or int(len(slist) * proportion), PROTOCOL
                )
            )

    taus = [r.diff_tau for r in results if r.diff_tau is not None]
    return MainResult(
        avg_score=np.average([r.avg_score for r in results]),
        avg_perfect=None,
        diff_tau=np.average(taus) if taus else None,
        diff_pearson=None,
    )


# =====================================================================
# QE 모델 로드 및 추론 로직
# =====================================================================


def load_xcomet():
    import comet

    logger.info(f"Loading XCOMET: {XCOMET_MODEL_NAME}...")
    torch.set_default_dtype(torch.bfloat16)
    model_path = comet.download_model(XCOMET_MODEL_NAME)
    model = comet.load_from_checkpoint(model_path)
    torch.set_default_dtype(torch.float32)
    model.to(torch.bfloat16)
    model.eval()
    return model


def load_metricx():
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

    logger.info(f"Loading MetricX: {METRICX_MODEL_NAME}...")
    tokenizer = AutoTokenizer.from_pretrained(METRICX_MODEL_NAME)
    model = AutoModelForSeq2SeqLM.from_pretrained(
        METRICX_MODEL_NAME, device_map="auto", torch_dtype=torch.bfloat16
    )
    model.eval()
    return tokenizer, model


def score_with_xcomet(model, sources, translations):
    torch.cuda.empty_cache()
    data = [{"src": s, "mt": t} for s, t in zip(sources, translations)]
    gpus_to_use = 1 if torch.cuda.is_available() else 0
    with torch.cuda.amp.autocast(dtype=torch.bfloat16):
        outputs = model.predict(data, batch_size=BATCH_SIZE, gpus=gpus_to_use)
    return outputs.scores if hasattr(outputs, "scores") else outputs


def score_with_metricx(tokenizer, model, sources, translations):
    scores = []
    for i in tqdm(range(0, len(sources), BATCH_SIZE), desc="MetricX-XXL"):
        batch_src, batch_mt = (
            sources[i : i + BATCH_SIZE],
            translations[i : i + BATCH_SIZE],
        )
        input_texts = [
            f"candidate: {mt} source: {src}" for mt, src in zip(batch_mt, batch_src)
        ]
        inputs = tokenizer(
            input_texts, return_tensors="pt", padding=True, truncation=True
        ).to(model.device)
        with torch.no_grad():
            decoder_input_ids = torch.tensor([[0]] * len(input_texts)).to(model.device)
            outputs = model(**inputs, decoder_input_ids=decoder_input_ids)
            batch_scores = outputs.logits[:, 0, 250089].cpu().tolist()
            scores.extend([max(0.0, min(25.0, s)) for s in batch_scores])
        del inputs, decoder_input_ids, outputs
        torch.cuda.empty_cache()
    return scores


# =====================================================================
# 메인 실행 로직
# =====================================================================
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--metric", type=str, choices=["XCOMET-XXL", "MetricX-XXL"], required=True
    )
    parser.add_argument(
        "--target_type", type=str, choices=["llms", "ref", "true"], required=True
    )
    args = parser.parse_args()

    data = Data.load(
        dataset_name="wmt24", lps=["all"], domains="all", protocol=PROTOCOL
    )

    if args.metric == "XCOMET-XXL":
        model = load_xcomet()
        score_fn = lambda src, mt: score_with_xcomet(model, src, mt)
    else:
        tokenizer, model = load_metricx()
        score_fn = lambda src, mt: score_with_metricx(tokenizer, model, src, mt)

    for lp, src_list in data.lp2src_data_list.items():
        if args.target_type == "llms":
            targets = WMT24_LLMS
        elif args.target_type == "ref":
            targets = WMT24_REF
        else:  # true crowd
            targets = list(
                set([sys for d in src_list for sys in d["scores"] if sys != "human"])
            )

        for d in src_list:
            scores_to_avg = []
            for t_name in targets:
                if t_name in d["scores"]:
                    mt = d["scores"][t_name]["mt"]
                    qe_score = score_fn([d["src"]], [mt])[0]
                    scores_to_avg.append(qe_score)
            d["scores"][f"ESTIMATED_{args.metric}"] = (
                np.mean(scores_to_avg) if scores_to_avg else 0.0
            )

    res = main_eval_avg_local(
        f"ESTIMATED_{args.metric}",
        data,
        single_src_subset=False,
        is_method_tgt_lang_dep=True,
        proportion=0.25,
    )
    print(
        f"\n>>> RESULT [{args.metric} on {args.target_type}]: DEC = {res.diff_tau:.4f}"
    )


if __name__ == "__main__":
    main()
