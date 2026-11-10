"""13. 오디오 생성: Suno API 호출 템플릿

텍스트→오디오(text-to-audio / text-to-music):
- 장르·분위기·길이·보컬 유무를 구체적으로 쓸수록
  원하는 결과에 가까워집니다.

중요:
- Suno는 공식 API/권한 환경에 따라 호출 방법이 달라질 수 있습니다.
- 아래는 승인된 API 엔드포인트가 제공된 경우의 requests 템플릿입니다.
- URL/키는 수업 환경 값으로 교체하세요.

필요 패키지 / 환경변수:
  pip install requests
  PowerShell: $env:SUNO_API_URL='...' ; $env:SUNO_API_KEY='...'
"""

import os

import requests


# ------------------------------------------------------------
# 기본 설정값 (수업/실습용)
# ------------------------------------------------------------
DEFAULT_PROMPT = "Warm lo-fi instrumental, 20 seconds, no vocals"
DEFAULT_TIMEOUT = 60


def get_suno_credentials(
    url_env="SUNO_API_URL",
    key_env="SUNO_API_KEY",
):
    """환경변수에서 Suno API URL과 키를 읽습니다.

    둘 다 있어야 호출할 수 있습니다.
    """
    url = os.environ.get(url_env)
    key = os.environ.get(key_env)
    return url, key


def require_credentials(url, key):
    """자격 증명이 없으면 초보자용 안내와 함께 종료합니다."""
    if url and key:
        return
    raise SystemExit(
        "SUNO_API_URL 및 SUNO_API_KEY를 설정하세요.\n"
        "PowerShell 예:\n"
        "  $env:SUNO_API_URL='...'\n"
        "  $env:SUNO_API_KEY='...'"
    )


def generate_audio(
    url,
    key,
    prompt,
    timeout=DEFAULT_TIMEOUT,
):
    """텍스트 프롬프트로 오디오 생성을 요청합니다.

    - headers Authorization Bearer: API 키로 본인임을 증명
    - json prompt: 어떤 음악을 만들지 설명하는 문장
    - timeout: 오디오 생성은 이미지보다 오래 걸릴 수 있음
    """
    if not prompt or not str(prompt).strip():
        raise ValueError("프롬프트가 비어 있습니다.")

    response = requests.post(
        url,
        headers={"Authorization": f"Bearer {key}"},
        json={"prompt": prompt},
        timeout=timeout,
    )
    # raise_for_status: HTTP 오류(4xx/5xx)면 예외를 발생시킴
    response.raise_for_status()
    return response.json()


def print_audio_report(prompt, result):
    """생성 요청 결과를 읽기 쉽게 출력합니다."""
    print(f"[프롬프트] {prompt}")
    print("[응답 JSON]")
    print(result)
    print()
    print("관찰 포인트:")
    print("  - 장르·분위기·길이·보컬 여부를 구체적으로 쓰면 결과가 안정됩니다.")
    print("  - 실제 응답 형식(URL, job id 등)은 수업에서 쓰는 API 문서를 따릅니다.")
    print("  - 키가 노출되지 않도록 환경변수로만 관리하세요.")


def run_audio_demo(prompt=DEFAULT_PROMPT, timeout=DEFAULT_TIMEOUT):
    """자격 증명 확인 → 생성 요청 → 결과 출력까지 한 번에 실행합니다.

    이 함수만 호출해도 전체 실습 흐름이 실행됩니다.
    """
    url, key = get_suno_credentials()
    require_credentials(url, key)
    result = generate_audio(url, key, prompt, timeout=timeout)
    print_audio_report(prompt, result)
    return result


def read_prompt_from_input():
    """사용자에게 오디오 프롬프트를 입력받습니다."""
    print("오디오/음악 생성 프롬프트를 입력하세요. (영어 권장)")
    print(f"(빈 입력이면 기본 예제 사용: {DEFAULT_PROMPT})")
    line = input("> ").strip()
    return line or DEFAULT_PROMPT


if __name__ == "__main__":
    # --------------------------------------------------
    # A. 기본 데모: lo-fi 짧은 연주곡 요청
    # --------------------------------------------------
    print("=" * 60)
    print("A. 기본 데모 (Suno 오디오 생성 템플릿)")
    print("=" * 60)
    run_audio_demo()
    print()

    # --------------------------------------------------
    # B. 일반화: 사용자가 입력한 프롬프트로 같은 절차 반복
    # --------------------------------------------------
    print("=" * 60)
    print("B. 직접 입력한 프롬프트로 오디오 생성하기")
    print("=" * 60)
    user_prompt = read_prompt_from_input()
    print()
    run_audio_demo(prompt=user_prompt)
