"""08. Masked Language Modeling: 가려진 토큰 복원

Masked Language Modeling (MLM)이란?
- 문장에서 일부 토큰을 [MASK]로 가린 뒤, 양옆 문맥을 보고 원래 단어를 예측합니다.
- BERT 사전학습의 핵심 과제입니다.
- GPT의 다음 토큰 예측(왼쪽→오른쪽만 봄)과 달리,
  BERT는 앞뒤 문맥을 모두 사용합니다.

필요 패키지:
  pip install transformers torch
"""

import os
import sys
from pathlib import Path


sys.stdout.reconfigure(encoding="utf-8")


def setup_windows_torch_dll():
    """Windows에서 torch DLL을 찾을 수 있도록 검색 경로를 보강합니다."""
    if sys.platform != "win32":
        return
    torch_lib = Path(sys.prefix) / "Lib" / "site-packages" / "torch" / "lib"
    if torch_lib.exists():
        os.add_dll_directory(str(torch_lib))
        os.environ["PATH"] = str(torch_lib) + os.pathsep + os.environ.get("PATH", "")


setup_windows_torch_dll()
from transformers import pipeline


# ------------------------------------------------------------
# 기본 설정값 (수업/실습용)
# ------------------------------------------------------------
# bert-base-uncased는 영어 전용이라 독일어에 약합니다.
# 아래 모델은 독일어 위키·뉴스 등으로 학습된 BERT (대소문자 구분, cased).
# 처음 실행 시 모델 가중치를 인터넷에서 다운로드합니다.
DEFAULT_MODEL_NAME = "dbmdz/bert-base-german-cased"

# 예문: Paris ist die [MASK] von Frankreich.
#   [MASK] 자리에 올 단어 후보와 확률을 출력
#   기대: Hauptstadt (수도)
DEFAULT_SENTENCE = "Paris ist die [MASK] von Frankreich."
DEFAULT_TOP_K = 3


def load_fill_mask(model_name=DEFAULT_MODEL_NAME):
    """fill-mask 파이프라인을 불러옵니다."""
    return pipeline("fill-mask", model=model_name)


def fill_masked_sentence(fill, sentence, top_k=DEFAULT_TOP_K):
    """[MASK]가 포함된 문장의 상위 후보를 반환합니다.

    반환 항목 예:
    - token_str : 예측된 단어(토큰)
    - score     : 모델이 부여한 확률
    """
    if "[MASK]" not in sentence:
        raise ValueError("문장에 [MASK]가 있어야 합니다. 예: Paris ist die [MASK] von Frankreich.")
    results = fill(sentence)
    return results[:top_k]


def print_fill_mask_report(sentence, results, digits=3):
    """예측 후보를 초보자가 읽기 쉽게 출력합니다."""
    print(f"문장: {sentence}")
    print(f"상위 {len(results)}개 예측:")
    for i, result in enumerate(results, start=1):
        token = result["token_str"]
        score = result["score"]
        print(f"  ({i}) {token!r:20s}  확률={score:.{digits}f}")
    print()
    print("관찰 포인트:")
    print("  - 앞뒤 문맥을 모두 보고 [MASK]를 채웁니다.")
    print("  - 가장 높은 확률이 '정답'을 보장하지는 않습니다.")
    print("  - 다음 토큰만 예측하는 GPT와 목적이 다릅니다.")


def run_fill_mask_demo(
    sentence=DEFAULT_SENTENCE,
    model_name=DEFAULT_MODEL_NAME,
    top_k=DEFAULT_TOP_K,
):
    """한 문장에 대해 MLM을 실행하고 결과를 출력합니다.

    이 함수만 호출해도 전체 실습 흐름이 실행됩니다.
    """
    print(f"모델 불러오는 중: {model_name}")
    fill = load_fill_mask(model_name)
    print()

    results = fill_masked_sentence(fill, sentence, top_k=top_k)
    print_fill_mask_report(sentence, results)
    return results


def read_masked_sentence():
    """사용자에게 [MASK]가 포함된 문장을 입력받습니다."""
    print("[MASK]가 포함된 문장을 입력하세요.")
    print(f"(빈 입력이면 기본 예제 사용: {DEFAULT_SENTENCE})")
    line = input("> ").strip()
    return line or DEFAULT_SENTENCE


if __name__ == "__main__":
    # --------------------------------------------------
    # A. 기본 데모: 수도(Hauptstadt) 예측
    # --------------------------------------------------
    print("=" * 60)
    print("A. 기본 데모 ([MASK] = 수도)")
    print("=" * 60)
    run_fill_mask_demo()
    print()

    # --------------------------------------------------
    # B. 일반화: 사용자가 입력한 문장으로 같은 절차 반복
    # --------------------------------------------------
    print("=" * 60)
    print("B. 직접 입력한 문장으로 [MASK] 채우기")
    print("=" * 60)
    user_sentence = read_masked_sentence()
    print()
    run_fill_mask_demo(sentence=user_sentence)
