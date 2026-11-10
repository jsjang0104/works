"""14. 동영상 생성: API 기반 생성 요청의 일반적 패턴

텍스트→비디오(text-to-video):
- 장면·카메라 움직임·길이·화면비를 구체적으로 쓸수록
  원하는 결과에 가까워집니다.

중요:
- 서비스별 모델명·엔드포인트·비동기 상태조회 방식은 문서를 확인하세요.
- 많은 동영상 API는 즉시 파일을 주지 않고 작업 ID만 반환합니다(비동기).

필요 패키지 / 환경변수:
  pip install requests
  PowerShell: $env:VIDEO_API_URL='...' ; $env:VIDEO_API_KEY='...'
"""

import os

import requests


# ------------------------------------------------------------
# 기본 설정값 (수업/실습용)
# ------------------------------------------------------------
DEFAULT_PROMPT = "A 5-second cinematic shot of a robot reading in a library"
DEFAULT_DURATION_SECONDS = 5
DEFAULT_ASPECT_RATIO = "16:9"
DEFAULT_TIMEOUT = 60


def get_video_credentials(
    url_env="VIDEO_API_URL",
    key_env="VIDEO_API_KEY",
):
    """환경변수에서 동영상 API URL과 키를 읽습니다."""
    url = os.environ.get(url_env)
    key = os.environ.get(key_env)
    return url, key


def require_credentials(url, key):
    """자격 증명이 없으면 초보자용 안내와 함께 종료합니다."""
    if url and key:
        return
    raise SystemExit(
        "VIDEO_API_URL 및 VIDEO_API_KEY를 설정하세요.\n"
        "PowerShell 예:\n"
        "  $env:VIDEO_API_URL='...'\n"
        "  $env:VIDEO_API_KEY='...'"
    )


def build_payload(
    prompt,
    duration_seconds=DEFAULT_DURATION_SECONDS,
    aspect_ratio=DEFAULT_ASPECT_RATIO,
):
    """서버에 보낼 생성 조건(JSON payload)을 만듭니다.

    - prompt            : 어떤 장면을 찍을지 설명하는 문장
    - duration_seconds  : 영상 길이(초). 길수록 비용·대기 시간이 늘어남
    - aspect_ratio      : 화면비. 16:9=가로형, 9:16=세로형
    """
    if not prompt or not str(prompt).strip():
        raise ValueError("프롬프트가 비어 있습니다.")
    return {
        "prompt": prompt,
        "duration_seconds": duration_seconds,
        "aspect_ratio": aspect_ratio,
    }


def generate_video(
    url,
    key,
    payload,
    timeout=DEFAULT_TIMEOUT,
):
    """동영상 생성 요청을 보내고 JSON 응답을 반환합니다.

    많은 API는 작업 ID만 먼저 주고, 별도 상태조회가 필요합니다.
    """
    response = requests.post(
        url,
        headers={"Authorization": f"Bearer {key}"},
        json=payload,
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()


def print_video_report(payload, result):
    """생성 요청 결과를 읽기 쉽게 출력합니다."""
    print("[요청 payload]")
    print(payload)
    print("[응답 JSON]")
    print(result)
    print()
    print("관찰 포인트:")
    print("  - 장면·카메라·길이·화면비를 구체적으로 쓰면 결과가 안정됩니다.")
    print("  - 응답이 job id라면, 완료될 때까지 상태조회 API를 추가로 호출합니다.")
    print("  - 키가 노출되지 않도록 환경변수로만 관리하세요.")


def run_video_demo(
    prompt=DEFAULT_PROMPT,
    duration_seconds=DEFAULT_DURATION_SECONDS,
    aspect_ratio=DEFAULT_ASPECT_RATIO,
    timeout=DEFAULT_TIMEOUT,
):
    """자격 증명 확인 → payload 구성 → 요청 → 결과 출력까지 실행합니다.

    이 함수만 호출해도 전체 실습 흐름이 실행됩니다.
    """
    url, key = get_video_credentials()
    require_credentials(url, key)

    payload = build_payload(
        prompt,
        duration_seconds=duration_seconds,
        aspect_ratio=aspect_ratio,
    )
    result = generate_video(url, key, payload, timeout=timeout)
    print_video_report(payload, result)
    return result


def read_video_options():
    """사용자에게 프롬프트와 간단한 옵션을 입력받습니다."""
    print("동영상 생성 프롬프트를 입력하세요. (영어 권장)")
    print(f"(빈 입력이면 기본 예제 사용: {DEFAULT_PROMPT})")
    prompt = input("> ").strip() or DEFAULT_PROMPT

    duration_text = input(f"길이(초, 기본 {DEFAULT_DURATION_SECONDS}): ").strip()
    duration = int(duration_text) if duration_text else DEFAULT_DURATION_SECONDS

    ratio = input(f"화면비(기본 {DEFAULT_ASPECT_RATIO}): ").strip() or DEFAULT_ASPECT_RATIO
    return prompt, duration, ratio


if __name__ == "__main__":
    # --------------------------------------------------
    # A. 기본 데모: 5초 시네마틱 장면 요청
    # --------------------------------------------------
    print("=" * 60)
    print("A. 기본 데모 (동영상 생성 요청 템플릿)")
    print("=" * 60)
    run_video_demo()
    print()

    # --------------------------------------------------
    # B. 일반화: 사용자가 입력한 조건으로 같은 절차 반복
    # --------------------------------------------------
    print("=" * 60)
    print("B. 직접 입력한 조건으로 동영상 생성하기")
    print("=" * 60)
    user_prompt, user_duration, user_ratio = read_video_options()
    print()
    run_video_demo(
        prompt=user_prompt,
        duration_seconds=user_duration,
        aspect_ratio=user_ratio,
    )
