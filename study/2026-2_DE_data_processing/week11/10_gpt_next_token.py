"""10. GPT: 자동회귀 방식의 다음 토큰 생성

GPT의 생성 방식: 자동회귀(autoregressive, AR)
- 지금까지 나온 토큰만 보고(왼쪽→오른쪽) 다음 토큰 1개를 예측합니다.
- 그 토큰을 문장 끝에 붙인 뒤, 다시 다음 토큰을 예측하는 일을 반복합니다.
- 08번의 BERT(MLM)는 앞뒤 문맥을 모두 보지만,
  GPT는 앞(왼쪽)만 보고 뒤를 이어 씁니다 → 텍스트 생성에 적합합니다.

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
# distilgpt2는 영어 전용이라 독일어에 약합니다.
# 아래 모델은 독일어로 학습된 GPT-2 (dbmdz: 바이에른 주립도서관 ML 팀).
# 처음 실행 시 모델 가중치를 인터넷에서 다운로드합니다.
DEFAULT_MODEL_NAME = "dbmdz/german-gpt2"
DEFAULT_PROMPT = "Künstliche Intelligenz wird"
DEFAULT_MAX_NEW_TOKENS = 20
DEFAULT_TEMPERATURE = 0.8


def load_generator(model_name=DEFAULT_MODEL_NAME):
    """text-generation 파이프라인을 불러옵니다."""
    return pipeline("text-generation", model=model_name)


def generate_text(
    generator,
    prompt,
    max_new_tokens=DEFAULT_MAX_NEW_TOKENS,
    temperature=DEFAULT_TEMPERATURE,
    do_sample=True,
):
    """프롬프트 뒤에 이어질 텍스트를 생성합니다.

    주요 매개변수
    - max_new_tokens : 새로 만들 토큰 개수 상한 (원문 길이 제외)
    - do_sample=True : 가장 높은 확률만 고르지 않고, 확률 분포에서 샘플링
    - temperature    : 값이 클수록 다양하고, 작을수록 보수적인 문장이 나옴
    """
    if not prompt or not str(prompt).strip():
        raise ValueError("프롬프트가 비어 있습니다.")
    results = generator(
        prompt,
        max_new_tokens=max_new_tokens,
        do_sample=do_sample,
        temperature=temperature,
    )
    return results[0]["generated_text"]


def print_generation_report(prompt, generated_text):
    """생성 결과를 읽기 쉽게 출력합니다."""
    print(f"[프롬프트] {prompt}")
    print(f"[생성 결과] {generated_text}")
    print()
    print("관찰 포인트:")
    print("  - 모델은 '다음 토큰'을 반복 예측해 문장을 이어 씁니다.")
    print("  - temperature가 높을수록 결과가 더 다양해질 수 있습니다.")
    print("  - 작은 로컬 모델이라 품질이 최신 LLM보다 낮을 수 있습니다.")


def run_generation_demo(
    prompt=DEFAULT_PROMPT,
    model_name=DEFAULT_MODEL_NAME,
    max_new_tokens=DEFAULT_MAX_NEW_TOKENS,
    temperature=DEFAULT_TEMPERATURE,
):
    """프롬프트 하나를 생성하고 결과를 출력합니다.

    이 함수만 호출해도 전체 실습 흐름이 실행됩니다.
    """
    print(f"모델 불러오는 중: {model_name}")
    generator = load_generator(model_name)
    print()

    generated = generate_text(
        generator,
        prompt,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
    )
    print_generation_report(prompt, generated)
    return generated


def read_prompt_and_options():
    """사용자에게 프롬프트와 간단한 생성 옵션을 입력받습니다."""
    print("이어서 쓸 프롬프트를 입력하세요.")
    print(f"(빈 입력이면 기본 예제 사용: {DEFAULT_PROMPT})")
    prompt = input("> ").strip() or DEFAULT_PROMPT

    temp_text = input(f"temperature (기본 {DEFAULT_TEMPERATURE}): ").strip()
    temperature = float(temp_text) if temp_text else DEFAULT_TEMPERATURE

    tokens_text = input(f"max_new_tokens (기본 {DEFAULT_MAX_NEW_TOKENS}): ").strip()
    max_new_tokens = int(tokens_text) if tokens_text else DEFAULT_MAX_NEW_TOKENS

    return prompt, temperature, max_new_tokens


if __name__ == "__main__":
    # --------------------------------------------------
    # A. 기본 데모: 고정 프롬프트로 이어 쓰기
    # --------------------------------------------------
    print("=" * 60)
    print("A. 기본 데모 (독일어 GPT-2 이어 쓰기)")
    print("=" * 60)
    run_generation_demo()
    print()

    # --------------------------------------------------
    # B. 일반화: 사용자가 입력한 프롬프트로 같은 절차 반복
    # --------------------------------------------------
    print("=" * 60)
    print("B. 직접 입력한 프롬프트로 생성하기")
    print("=" * 60)
    user_prompt, user_temp, user_tokens = read_prompt_and_options()
    print()
    run_generation_demo(
        prompt=user_prompt,
        temperature=user_temp,
        max_new_tokens=user_tokens,
    )
