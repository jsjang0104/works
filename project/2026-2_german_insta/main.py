"""Run with python main.py; all interactive input stays in the terminal."""

import unicodedata
from collections.abc import Callable
from datetime import UTC, date, datetime
from pathlib import Path

import settings
from cards import make_caption, render_card, reserve_output, save_image

MANUAL_MESSAGE = "직접 독일어 문장을 입력해주세요."


def _read(prompt: str, *, limit: int, input_fn: Callable, output_fn: Callable) -> str:
    while True:
        value = unicodedata.normalize("NFC", " ".join(input_fn(prompt).split()))
        if not value:
            output_fn("빈 값은 사용할 수 없습니다. 다시 입력해 주세요.")
        elif len(value) > limit:
            output_fn(f"{limit}자 이내로 입력해 주세요.")
        else:
            return value


def _confirm(draft: str, label: str, input_fn: Callable, output_fn: Callable) -> str:
    output_fn(f"{label}: {draft}")
    while True:
        edited = unicodedata.normalize(
            "NFC",
            " ".join(
                input_fn(f"Enter로 확정하거나 수정한 {label}을 입력하세요: ").split()
            ),
        )
        if len(edited) <= 400:
            return edited or draft
        output_fn("400자 이내로 입력해 주세요.")


def image_prompt(sentence: str) -> str:
    return (
        "Create a warm, detailed editorial illustration of this German sentence. "
        "No text or lettering in the image. "
        "Never include any words, letters, captions, signs, speech bubbles, signatures, "
        "or watermarks. "
        f"Scene: {sentence}"
    )


def _local_sentences(words: list[str]) -> list[dict[str, str]]:
    from local_llm import generate_sentences

    return generate_sentences(words)


def _mcp_image(prompt: str) -> bytes:
    from image_mcp import generate_image

    return generate_image(prompt)


def _image_with_recovery(
    prompt: str,
    generator: Callable,
    input_fn: Callable,
    output_fn: Callable,
) -> bytes | None:
    local_path = None
    while True:
        try:
            data = (
                local_path.expanduser().read_bytes()
                if local_path
                else generator(prompt)
            )
            # Validate while recovery options are still available.
            from io import BytesIO

            from PIL import Image

            with Image.open(BytesIO(data)) as image:
                image.verify()
            return data
        except (
            Exception
        ) as error:  # noqa: BLE001 -- recover at the interactive boundary
            output_fn(f"이미지를 준비하지 못했습니다: {error}")
            answer = input_fn(
                "다시 시도하려면 r, 기존 이미지 파일 경로, 건너뛰려면 Enter: "
            ).strip()
            if not answer:
                return None
            if answer.lower() == "r":
                continue
            local_path = Path(answer)


def run(
    *,
    root: Path = settings.PROJECT_DIR,
    today: date | None = None,
    input_fn: Callable = input,
    output_fn: Callable = print,
    sentence_generator: Callable | None = None,
    image_generator: Callable | None = None,
) -> int:
    day = today or datetime.now(UTC).astimezone().date()
    sentence_generator = sentence_generator or _local_sentences
    image_generator = image_generator or _mcp_image
    try:
        output_fn("독일어 단어 2개로 이미지 카드와 캡션을 만듭니다.")
        words = [
            _read(
                f"단어 {index + 1}: ", limit=80, input_fn=input_fn, output_fn=output_fn
            )
            for index in range(2)
        ]
        output_fn(
            "로컬 모델과 GPU 상태를 확인합니다. 사용 가능하면 독일어 문장과 한국어 해석을 생성합니다."
        )
        try:
            drafts = sentence_generator(words)
            if (
                not isinstance(drafts, list)
                or len(drafts) != 2
                or any(
                    not isinstance(pair, dict)
                    or any(
                        not isinstance(pair.get(key), str)
                        or not pair[key].strip()
                        or len(pair[key]) > 400
                        for key in ("german", "korean")
                    )
                    for pair in drafts
                )
            ):
                raise ValueError(
                    "사용할 수 있는 독일어 문장과 한국어 해석 두 쌍을 얻지 못했습니다."
                )
        except (
            Exception
        ) as error:  # noqa: BLE001 -- recover at the interactive boundary
            output_fn(f"자동 문장 생성을 사용할 수 없습니다: {error}")
            drafts = None
        sentences, translations = [], []
        if drafts is None:
            output_fn(MANUAL_MESSAGE)
            output_fn("한국어 해석도 직접 입력해 주세요.")
            for word in words:
                sentences.append(
                    _read(
                        f"[{word}]를 사용한 독일어 문장: ",
                        limit=400,
                        input_fn=input_fn,
                        output_fn=output_fn,
                    )
                )
                translations.append(
                    _read(
                        f"[{word}] 문장의 한국어 해석: ",
                        limit=400,
                        input_fn=input_fn,
                        output_fn=output_fn,
                    )
                )
        else:
            for word, draft in zip(words, drafts):
                original = unicodedata.normalize(
                    "NFC", " ".join(draft["german"].split())
                )
                output_fn(f"[{word}]")
                sentence = _confirm(original, "독일어 문장", input_fn, output_fn)
                used_model = sentence == original
                if used_model:
                    translation = _confirm(
                        unicodedata.normalize("NFC", " ".join(draft["korean"].split())),
                        "한국어 해석",
                        input_fn,
                        output_fn,
                    )
                else:
                    output_fn(
                        "독일어 문장을 수정했습니다. 수정한 문장의 한국어 해석을 직접 입력해 주세요."
                    )
                    translation = _read(
                        f"[{word}] 문장의 한국어 해석: ",
                        limit=400,
                        input_fn=input_fn,
                        output_fn=output_fn,
                    )
                sentences.append(sentence)
                translations.append(translation)

        # Save both ready-to-post captions before the first network request.
        outputs = [
            reserve_output(Path(root), word, make_caption(), day) for word in words
        ]
        output_fn(f"캡션 저장 위치: {outputs[0].caption.parent.resolve()}")
        completed = 0
        for index, (word, sentence, translation, paths) in enumerate(
            zip(words, sentences, translations, outputs)
        ):
            output_fn(f"[{index + 1}/2] {word}: 이미지를 준비합니다.")
            data = _image_with_recovery(
                image_prompt(sentence), image_generator, input_fn, output_fn
            )
            if data is None:
                output_fn(
                    f"이미지 생성을 건너뛰었습니다. 캡션은 저장되어 있습니다: {paths.caption.name}"
                )
                continue
            try:
                save_image(
                    paths.image,
                    render_card(data, word, sentence, translation, day.isoformat()),
                )
            except (
                Exception
            ) as error:  # noqa: BLE001 -- recover at the interactive boundary
                output_fn(f"카드를 저장하지 못했습니다: {error}. 캡션은 보존했습니다.")
                continue
            completed += 1
            output_fn(f"저장: {paths.image.name}, {paths.caption.name}")
        output_fn(
            f"이미지 {completed}/2장, 캡션 2개 저장. 인스타그램에는 직접 업로드해 주세요."
        )
        return 0 if completed == 2 else 1
    except (KeyboardInterrupt, EOFError):
        output_fn("\n입력을 취소했습니다. 이미 저장된 결과는 유지됩니다.")
        return 130
    except OSError as error:
        output_fn(f"파일을 저장할 수 없습니다: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(run())
