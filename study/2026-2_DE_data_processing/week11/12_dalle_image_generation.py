"""12. 이미지 생성: DALL·E 3 API 호출(OPENAI_API_KEY 필요)

텍스트→이미지(text-to-image):
- 프롬프트(설명문)를 넣으면 그에 맞는 그림을 만듭니다.
- 스타일·색·구도·넣을/빼야 할 요소를 구체적으로 쓸수록
  원하는 결과에 가까워집니다.

주의:
- 생성 이미지 URL은 일정 시간 후 만료될 수 있습니다.
- 수업 자료로 남기려면 URL을 받은 뒤 바로 저장하세요.

필요 패키지 / 환경변수:
  pip install openai
  PowerShell: $env:OPENAI_API_KEY='...'
"""

from openai import OpenAI


# ------------------------------------------------------------
# 기본 설정값 (수업/실습용)
# ------------------------------------------------------------
DEFAULT_MODEL_NAME = "dall-e-3"
DEFAULT_SIZE = "1024x1024"
DEFAULT_QUALITY = "standard"

# 예문: Transformer 어텐션을 설명하는 교육용 일러스트
#   수업 06번에서 배운 개념을 그림으로 시각화하라는 요청
#   "no text": 생성 모델은 그림 속 글자를 잘 못 쓰므로 글자 없이 그리라고 명시
DEFAULT_PROMPT = (
    "A clean educational illustration of a Transformer attention mechanism, "
    "blue and gold, no text"
)


def create_client():
    """OpenAI 클라이언트를 만듭니다. (OPENAI_API_KEY 필요)"""
    return OpenAI()


def generate_image(
    client,
    prompt,
    model_name=DEFAULT_MODEL_NAME,
    size=DEFAULT_SIZE,
    quality=DEFAULT_QUALITY,
    n=1,
):
    """텍스트 프롬프트로 이미지를 생성하고 응답 객체를 반환합니다.

    주요 매개변수
    - model   : 이미지 모델 이름
    - prompt  : 어떤 그림을 그릴지 설명하는 문장
    - size    : 출력 해상도 (DALL·E 3는 1024x1024, 1024x1792, 1792x1024)
    - quality : standard(기본) 또는 hd(더 선명, 비용↑)
    - n       : 한 번에 만들 이미지 개수 (DALL·E 3는 n=1만 지원)
    """
    if not prompt or not str(prompt).strip():
        raise ValueError("프롬프트가 비어 있습니다.")

    return client.images.generate(
        model=model_name,
        prompt=prompt,
        size=size,
        quality=quality,
        n=n,
    )


def extract_image_url(response):
    """응답에서 첫 번째 이미지 URL을 꺼냅니다."""
    return response.data[0].url


def print_image_report(prompt, image_url, model_name=DEFAULT_MODEL_NAME):
    """생성 결과를 읽기 쉽게 출력합니다."""
    print(f"[모델] {model_name}")
    print(f"[프롬프트] {prompt}")
    print(f"[이미지 URL] {image_url}")
    print()
    print("관찰 포인트:")
    print("  - 구체적일수록(색, 구도, 스타일) 원하는 결과에 가까워집니다.")
    print("  - 그림 속 글자는 잘 안 나오므로 'no text'를 명시하는 편이 안전합니다.")
    print("  - URL은 만료될 수 있으니 필요하면 바로 저장하세요.")


def run_image_demo(
    prompt=DEFAULT_PROMPT,
    model_name=DEFAULT_MODEL_NAME,
    size=DEFAULT_SIZE,
    quality=DEFAULT_QUALITY,
):
    """이미지 생성을 실행하고 URL을 출력합니다.

    이 함수만 호출해도 전체 실습 흐름이 실행됩니다.
    """
    client = create_client()
    response = generate_image(
        client,
        prompt,
        model_name=model_name,
        size=size,
        quality=quality,
    )
    image_url = extract_image_url(response)
    print_image_report(prompt, image_url, model_name=model_name)
    return image_url


def read_prompt_from_input():
    """사용자에게 이미지 프롬프트를 입력받습니다."""
    print("이미지 생성 프롬프트를 입력하세요. (영어 권장)")
    print("(빈 입력이면 기본 예제 사용)")
    line = input("> ").strip()
    return line or DEFAULT_PROMPT


if __name__ == "__main__":
    # --------------------------------------------------
    # A. 기본 데모: Attention 교육용 일러스트
    # --------------------------------------------------
    print("=" * 60)
    print("A. 기본 데모 (DALL·E 3 이미지 생성)")
    print("=" * 60)
    run_image_demo()
    print()

    # --------------------------------------------------
    # B. 일반화: 사용자가 입력한 프롬프트로 같은 절차 반복
    # --------------------------------------------------
    print("=" * 60)
    print("B. 직접 입력한 프롬프트로 이미지 생성하기")
    print("=" * 60)
    user_prompt = read_prompt_from_input()
    print()
    run_image_demo(prompt=user_prompt)
