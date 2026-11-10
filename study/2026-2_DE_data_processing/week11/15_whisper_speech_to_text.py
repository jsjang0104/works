"""15. Whisper: 음성 파일을 텍스트로 전사

전사(transcription)란?
- 말한 내용을 글로 받아 적는 것입니다.
- 번역(translation)과는 다릅니다.
  예) 독일어로 말하면 독일어 글로 나옵니다.

13번의 Suno는 텍스트→오디오(생성)였고,
여기서는 반대로 오디오→텍스트(전사)를 합니다.

필요 패키지 / 환경변수:
  pip install openai
  PowerShell: $env:OPENAI_API_KEY='...'

기본 전제:
  같은 폴더에 sample.mp3가 있어야 합니다. (또는 경로를 직접 입력)
"""

from pathlib import Path

from openai import OpenAI


# ------------------------------------------------------------
# 기본 설정값 (수업/실습용)
# ------------------------------------------------------------
DEFAULT_MODEL_NAME = "whisper-1"
DEFAULT_AUDIO_PATH = "sample.mp3"
DEFAULT_LANGUAGE = "de"  # 독일어


def create_client():
    """OpenAI 클라이언트를 만듭니다. (OPENAI_API_KEY 필요)"""
    return OpenAI()


def transcribe_audio(
    client,
    audio_path,
    model_name=DEFAULT_MODEL_NAME,
    language=DEFAULT_LANGUAGE,
):
    """음성 파일을 텍스트로 전사합니다.

    - 'rb': 오디오는 바이너리이므로 읽기+바이너리 모드로 엽니다.
    - language: 음성의 언어 코드. 'de'는 독일어.
                언어를 알려 주면 인식 정확도가 올라갑니다.
    """
    path = Path(audio_path)
    if not path.exists():
        raise FileNotFoundError(
            f"음성 파일을 찾을 수 없습니다: {path}\n"
            "같은 폴더에 sample.mp3를 두거나, 올바른 경로를 입력하세요."
        )

    with open(path, "rb") as audio:
        response = client.audio.transcriptions.create(
            model=model_name,
            file=audio,
            language=language,
        )
    return response.text


def print_transcription_report(audio_path, text, language=DEFAULT_LANGUAGE):
    """전사 결과를 읽기 쉽게 출력합니다."""
    print(f"[파일] {audio_path}")
    print(f"[언어] {language}")
    print("[전사 결과]")
    print(text)
    print()
    print("관찰 포인트:")
    print("  - 전사는 '말한 내용 → 같은 언어의 글'입니다. (번역이 아님)")
    print("  - 언어 코드를 주면 인식이 더 안정적인 경우가 많습니다.")
    print("  - 잡음이 많거나 발음이 불명확하면 오류가 날 수 있습니다.")


def run_transcription_demo(
    audio_path=DEFAULT_AUDIO_PATH,
    model_name=DEFAULT_MODEL_NAME,
    language=DEFAULT_LANGUAGE,
):
    """전사 전체 흐름을 한 번에 실행합니다.

    이 함수만 호출해도 전체 실습 흐름이 실행됩니다.
    """
    client = create_client()
    text = transcribe_audio(
        client,
        audio_path,
        model_name=model_name,
        language=language,
    )
    print_transcription_report(audio_path, text, language=language)
    return text


def read_audio_options():
    """사용자에게 파일 경로와 언어 코드를 입력받습니다."""
    print("음성 파일 경로를 입력하세요.")
    print(f"(빈 입력이면 기본 예제 사용: {DEFAULT_AUDIO_PATH})")
    audio_path = input("> ").strip() or DEFAULT_AUDIO_PATH

    language = input(f"언어 코드(기본 {DEFAULT_LANGUAGE}): ").strip() or DEFAULT_LANGUAGE
    return audio_path, language


if __name__ == "__main__":
    # --------------------------------------------------
    # A. 기본 데모: sample.mp3 를 독일어로 전사
    # --------------------------------------------------
    print("=" * 60)
    print("A. 기본 데모 (Whisper 전사)")
    print("=" * 60)
    try:
        run_transcription_demo()
    except FileNotFoundError as exc:
        print(exc)
        print("B단계에서 다른 파일 경로를 입력해 보세요.")
    print()

    # --------------------------------------------------
    # B. 일반화: 사용자가 지정한 파일로 같은 절차 반복
    # --------------------------------------------------
    print("=" * 60)
    print("B. 직접 지정한 파일로 전사하기")
    print("=" * 60)
    user_path, user_lang = read_audio_options()
    print()
    run_transcription_demo(audio_path=user_path, language=user_lang)
