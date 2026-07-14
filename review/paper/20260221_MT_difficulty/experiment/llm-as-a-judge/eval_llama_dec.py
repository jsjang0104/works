"""
Llama (vLLM) LLM-as-a-Judge DEC 평가 스크립트.

Llama 3.1 8B-Instruct CSV를 불러와
DEC (Difficulty Estimation Correlation) 점수를 계산
"""

import sys
from pathlib import Path
from typing import Literal

# ── path setup ─────────────────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import difficulty_estimation
import difficulty_estimation.evaluate
import difficulty_estimation.data
import subsampling.misc

# ── config ─────────────────────────────────────────────────────────────────────
protocol: Literal["esa", "mqm"] = "esa"
SINGLE_SRC_SUBSET = False

# Llama CSV 파일 경로
LLAMA_CSV_DIR = (
    Path(__file__).resolve().parent.parent.parent
    / "data"
    / "LLM-as-a-Judge"
    / protocol
    / "llama"
)


# ── main ───────────────────────────────────────────────────────────────────────


def main():
    # ── 1. 데이터 로드 ─────────────────────────────────────────────────────────
    print("Loading WMT24 data...")
    data = difficulty_estimation.data.Data.load(
        dataset_name="wmt24",
        lps=["all"],
        domains="all",
        protocol=protocol,
    )

    # ── 2. Llama LLM-as-a-Judge 스코어 적용 ──────────────────────────────────
    llama_tasks = [
        (
            "llama-3.1-8b-instruct_source_based_num_scores.csv",
            "Llama 3.1 8B, src-based",
        ),
        (
            "llama-3.1-8b-instruct_target_based_num_scores.csv",
            "Llama 3.1 8B, tgt-based",
        ),
    ]

    for csv_filename, llm_name in llama_tasks:
        csv_path = LLAMA_CSV_DIR / csv_filename
        if not csv_path.exists():
            print(f"  [SKIP] {csv_path} not found")
            continue
        print(f"  Loading: {csv_path.name} → '{llm_name}'")
        subsampling.misc.apply_llm_as_a_judge(
            data,
            scored_source_texts_df_path=csv_path,
            llm_name=llm_name,
        )

    # ── 3. DEC 계산 ──────────────────────────────────────────────────────────
    print(f"\n{'='*65}")
    print(f"  DEC (Difficulty Estimation Correlation) — Llama 3.1 8B-Instruct")
    print(f"{'='*65}")
    print(f"{'Method':<40} | {'DEC':>8}")
    print("-" * 55)

    methods = [
        # (display_name, internal_name, is_tgt_lang_dep)
        ("Llama 3.1 8B (src-based)", "LLM-as-a-Judge (Llama 3.1 8B, src-based)", False),
        ("Llama 3.1 8B (tgt-based)", "LLM-as-a-Judge (Llama 3.1 8B, tgt-based)", True),
    ]

    results_rows = []
    for display_name, internal_name, is_tgt_lang_dep in methods:
        try:
            res = difficulty_estimation.evaluate.main_eval_avg(
                internal_name,
                data=data,
                single_src_subset=SINGLE_SRC_SUBSET,
                is_method_tgt_lang_dep=is_tgt_lang_dep,
                protocol=protocol,
                proportion=0.25,
            )
            dec_val = res.diff_tau
            dec_str = f"{dec_val:.3f}" if dec_val is not None else "N/A"
            avg_str = f"{res.avg_score:.1f}"
            perf_str = f"{res.avg_perfect * 100:.1f}%"
        except Exception as e:
            dec_str = f"ERROR: {e}"
            avg_str = "N/A"
            perf_str = "N/A"

        print(f"{display_name:<40} | {dec_str:>8}")
        results_rows.append(
            {
                "method": display_name,
                "DEC": dec_str,
                "avg_score": avg_str,
                "perfect%": perf_str,
            }
        )

    print("-" * 55)

    # ── 4. 결과 저장 ─────────────────────────────────────────────────────────
    out_path = difficulty_estimation.ROOT / f"generated/llama_dec.txt"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        f.write(f"{'Method':<40} | {'DEC':>8} | {'AvgScore':>8} | {'Perfect%':>8}\n")
        f.write("-" * 75 + "\n")
        for row in results_rows:
            f.write(
                f"{row['method']:<40} | {row['DEC']:>8} | {row['avg_score']:>8} | {row['perfect%']:>8}\n"
            )

    print(f"\n→ Saved: {out_path}")
    print("Done!")


if __name__ == "__main__":
    main()
