"""07. BERT: 문장 쌍의 의미적 관계(NLI) 추론

NLI(Natural Language Inference, 자연어 추론)란?
- 전제(premise)가 참이라고 가정할 때, 가설(hypothesis)이 어떤 관계인지 분류합니다.
  - entailment    (함의) : 전제에서 논리적으로 따라 나옴
  - contradiction (모순) : 전제와 함께 참일 수 없음
  - neutral       (중립) : 전제만으로는 참/거짓을 판단할 수 없음

필요 패키지:
  pip install transformers torch sentencepiece
"""

import os
import sys
from pathlib import Path


# Windows 기본 콘솔(cp949)은 독일어 움라우트(ä, ö, ü)와 ß를 출력하지 못함
sys.stdout.reconfigure(encoding="utf-8")


def setup_windows_torch_dll():
    """Windows에서 torch DLL을 찾을 수 있도록 검색 경로를 보강합니다.

    그렇지 않으면 transformers를 import할 때
    OSError: [WinError 126] torch_python.dll 오류가 날 수 있습니다.
    """
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
# 영어 전용 모델은 독일어 문장에 약합니다.
# 아래 모델은 BERT 계열 다국어 인코더(mDeBERTa)를 XNLI로 미세조정한 것입니다.
# → 독일어를 포함한 여러 언어에서 문장 쌍의 관계를 분류할 수 있습니다.
# 처음 실행 시 모델 가중치를 인터넷에서 다운로드합니다.
DEFAULT_MODEL_NAME = "MoritzLaurer/mDeBERTa-v3-base-mnli-xnli"

# 전제: 한 학생이 독일어를 배운다
# (04_sentence_embedding.py의 예문과 같은 주제)
DEFAULT_PREMISE = "Ein Student lernt Deutsch."

# 세 가설: 함의 / 모순 / 중립을 한 번씩 보여 줌
DEFAULT_HYPOTHESES = [
    ("Eine Person studiert eine Sprache.", "함의(entailment) 기대"),
    ("Niemand lernt eine Sprache.", "모순(contradiction) 기대"),
    ("Das Wetter ist schön.", "중립(neutral) 기대"),
]


def load_nli_pipeline(model_name=DEFAULT_MODEL_NAME):
    """NLI용 text-classification 파이프라인을 불러옵니다."""
    return pipeline("text-classification", model=model_name)


def classify_pair(nli, premise, hypothesis):
    """전제-가설 한 쌍의 관계를 분류합니다.

    pipeline 입력:
    - text      = 전제
    - text_pair = 가설
    """
    if not premise or not str(premise).strip():
        raise ValueError("전제(premise)가 비어 있습니다.")
    if not hypothesis or not str(hypothesis).strip():
        raise ValueError("가설(hypothesis)가 비어 있습니다.")
    return nli({"text": premise, "text_pair": hypothesis})


def print_nli_result(premise, hypothesis, result, expected=None):
    """한 쌍의 추론 결과를 읽기 쉽게 출력합니다."""
    print(f"전제: {premise}")
    if expected:
        print(f"가설: {hypothesis}  ← {expected}")
    else:
        print(f"가설: {hypothesis}")
    print(f"결과: {result}")
    print()


def run_nli_demo(
    premise=DEFAULT_PREMISE,
    hypotheses=None,
    model_name=DEFAULT_MODEL_NAME,
):
    """여러 가설에 대해 NLI를 실행하고 결과를 출력합니다.

    이 함수만 호출해도 전체 실습 흐름이 실행됩니다.
    """
    if hypotheses is None:
        hypotheses = DEFAULT_HYPOTHESES

    print(f"모델 불러오는 중: {model_name}")
    nli = load_nli_pipeline(model_name)
    print()

    results = []
    for item in hypotheses:
        if isinstance(item, (tuple, list)) and len(item) >= 2:
            hypothesis, expected = item[0], item[1]
        else:
            hypothesis, expected = item, None
        result = classify_pair(nli, premise, hypothesis)
        print_nli_result(premise, hypothesis, result, expected=expected)
        results.append(result)

    print("관찰 포인트:")
    print("  - label 은 entailment / contradiction / neutral 중 하나입니다.")
    print("  - score 는 해당 라벨에 대한 모델의 확신도입니다.")
    print("  - 의미가 '비슷한지'와 '논리적으로 따라오는지'는 다른 개념입니다.")
    return results


def read_premise_and_hypotheses():
    """사용자에게 전제 1개와 가설 여러 개를 입력받습니다."""
    print("전제(premise)를 입력하세요. (빈 입력이면 기본 예제 사용)")
    premise = input("> ").strip() or DEFAULT_PREMISE

    print("가설(hypothesis)을 한 줄에 하나씩 입력하세요.")
    print("(빈 줄을 누르면 입력 종료 / 아무 것도 안 쓰면 기본 예제 사용)")
    hypotheses = []
    while True:
        line = input("> ").strip()
        if not line:
            break
        hypotheses.append((line, None))

    if not hypotheses:
        hypotheses = list(DEFAULT_HYPOTHESES)
    return premise, hypotheses


if __name__ == "__main__":
    # --------------------------------------------------
    # A. 기본 데모: 함의 / 모순 / 중립 예시
    # --------------------------------------------------
    print("=" * 60)
    print("A. 기본 데모 (함의 / 모순 / 중립)")
    print("=" * 60)
    run_nli_demo()
    print()

    # --------------------------------------------------
    # B. 일반화: 사용자가 입력한 전제·가설로 같은 절차 반복
    # --------------------------------------------------
    print("=" * 60)
    print("B. 직접 입력한 문장 쌍으로 추론하기")
    print("=" * 60)
    user_premise, user_hypotheses = read_premise_and_hypotheses()
    print()
    run_nli_demo(premise=user_premise, hypotheses=user_hypotheses)
