"""11. LLM: API 기반 질의(환경변수 OPENAI_API_KEY 필요)

LLM(Large Language Model, 대규모 언어 모델):
- 10번의 로컬 GPT-2는 작은 모델을 내 컴퓨터에서 돌렸습니다.
- 여기서는 OpenAI API로 훨씬 큰 모델에 질문을 보냅니다.

Prompting(프롬프팅):
- 모델에 넣는 입력 문장으로 출력의 언어·형식·길이를 조절합니다.
- 같은 내용이라도 "독일어로, 불릿 두 개로"처럼 조건을 주면
  답이 수업에서 다루기 쉬운 형태로 나옵니다.

필요 패키지 / 환경변수:
  pip install openai
  PowerShell: $env:OPENAI_API_KEY='...'
"""

import sys

from openai import OpenAI


sys.stdout.reconfigure(encoding="utf-8")


# ------------------------------------------------------------
# 기본 설정값 (수업/실습용)
# ------------------------------------------------------------
DEFAULT_MODEL_NAME = "gpt-4.1-mini"

# 예문: 03번에서 배운 코사인 유사도를 독일어로 짧게 설명하라고 요청
#   언어(Deutsch)와 형식(genau zwei Stichpunkte)을 프롬프트에 명시함
DEFAULT_PROMPT = (
    "Erklären Sie die Kosinusähnlichkeit in genau zwei Stichpunkten auf Deutsch."
)


def create_client():
    """OpenAI 클라이언트를 만듭니다.

    OPENAI_API_KEY가 환경변수로 설정되어 있어야 합니다.
    키가 없으면 이 단계에서 오류가 납니다.
    """
    return OpenAI()


def ask_llm(client, prompt, model_name=DEFAULT_MODEL_NAME):
    """프롬프트 하나를 LLM에 보내고 답변 문자열을 반환합니다.

    responses.create:
    - model : 사용할 모델 이름
    - input : 프롬프트(사용자 입력)
    """
    if not prompt or not str(prompt).strip():
        raise ValueError("프롬프트가 비어 있습니다.")

    response = client.responses.create(
        model=model_name,
        input=prompt,
    )
    return response.output_text


def print_llm_report(prompt, answer, model_name=DEFAULT_MODEL_NAME):
    """질문과 답을 읽기 쉽게 출력합니다."""
    print(f"[모델] {model_name}")
    print(f"[프롬프트] {prompt}")
    print("[답변]")
    print(answer)
    print()
    print("관찰 포인트:")
    print("  - 프롬프트에 언어·형식·길이를 명시하면 출력이 안정됩니다.")
    print("  - 같은 질문이라도 모델/온도 설정에 따라 답이 달라질 수 있습니다.")
    print("  - API 키와 사용량은 수업/개인 계정 정책을 확인하세요.")


def run_prompting_demo(prompt=DEFAULT_PROMPT, model_name=DEFAULT_MODEL_NAME):
    """한 번의 질의를 실행하고 결과를 출력합니다.

    이 함수만 호출해도 전체 실습 흐름이 실행됩니다.
    """
    client = create_client()
    answer = ask_llm(client, prompt, model_name=model_name)
    print_llm_report(prompt, answer, model_name=model_name)
    return answer


def read_prompt_from_input():
    """사용자에게 프롬프트를 입력받습니다."""
    print("LLM에 보낼 프롬프트를 입력하세요.")
    print("(빈 입력이면 기본 예제 사용)")
    line = input("> ").strip()
    return line or DEFAULT_PROMPT


if __name__ == "__main__":
    # --------------------------------------------------
    # A. 기본 데모: 코사인 유사도를 독일어 불릿 2개로 설명
    # --------------------------------------------------
    print("=" * 60)
    print("A. 기본 데모 (프롬프팅: 언어·형식 지정)")
    print("=" * 60)
    run_prompting_demo()
    print()

    # --------------------------------------------------
    # B. 일반화: 사용자가 입력한 프롬프트로 같은 절차 반복
    # --------------------------------------------------
    print("=" * 60)
    print("B. 직접 입력한 프롬프트로 질의하기")
    print("=" * 60)
    user_prompt = read_prompt_from_input()
    print()
    run_prompting_demo(prompt=user_prompt)
