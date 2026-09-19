import importlib
from datetime import date
from io import BytesIO

from PIL import Image

HASHTAGS = "#한국외대독일어과 #어휘와구문B2"
BODY = "FLUX Space MCP에 연결하여 AI 이미지를 생성하였습니다."
MANUAL_INPUT = [
    "Haus",
    "Baum",
    "Das Haus ist groß.",
    "그 집은 크다.",
    "Der Baum ist grün.",
    "그 나무는 푸르다.",
]
DRAFTS = [
    {"german": "Das Haus ist groß.", "korean": "그 집은 크다."},
    {"german": "Der Baum ist grün.", "korean": "그 나무는 푸르다."},
]


def subject():
    return importlib.import_module("main")


def png():
    data = BytesIO()
    Image.new("RGB", (256, 256), "#4c876a").save(data, "PNG")
    return data.getvalue()


def unavailable_llm(words):
    raise RuntimeError("Local LLM unavailable")


def expected_caption():
    return f"{HASHTAGS}\n\n{BODY}\n"


def test_busy_gpu_requests_both_languages_and_saves_manual_captions(
    tmp_path, monkeypatch
):
    app = subject()
    answers = iter(MANUAL_INPUT)
    output, rendered = [], []
    original = app.render_card

    def capture(data, word, sentence, translation, date_label):
        rendered.append((word, sentence, translation, date_label))
        return original(data, word, sentence, translation, date_label)

    monkeypatch.setattr(app, "render_card", capture)

    def no_gpu(words):
        raise RuntimeError("GPU belegt")

    result = app.run(
        root=tmp_path,
        today=date(2026, 9, 19),
        input_fn=lambda prompt: next(answers),
        output_fn=output.append,
        sentence_generator=no_gpu,
        image_generator=lambda prompt: png(),
    )
    folder = tmp_path / "2026-09-19"
    assert result == 0
    assert any("직접 독일어 문장을 입력해라" in line for line in output)
    assert any("한국어 해석" in line for line in output)
    assert rendered == [
        ("Haus", "Das Haus ist groß.", "그 집은 크다.", "2026-09-19"),
        ("Baum", "Der Baum ist grün.", "그 나무는 푸르다.", "2026-09-19"),
    ]
    assert len(list(folder.glob("*.jpg"))) == 2
    captions = list(folder.glob("*.txt"))
    assert len(captions) == 2
    assert all(p.read_text(encoding="utf-8") == expected_caption() for p in captions)


def test_default_run_checks_llm_then_accepts_manual_input_on_failure(tmp_path):
    app = subject()
    answers = iter(MANUAL_INPUT)

    calls = []

    def unavailable(words):
        calls.append(words)
        raise RuntimeError("Local LLM unavailable")

    assert (
        app.run(
            root=tmp_path,
            input_fn=lambda prompt: next(answers),
            output_fn=lambda text: None,
            sentence_generator=unavailable,
            image_generator=lambda prompt: png(),
        )
        == 0
    )
    assert all(p.read_text() == expected_caption() for p in tmp_path.rglob("*.txt"))

    assert calls == [["Haus", "Baum"]]


def test_accepted_and_replaced_sentences_get_same_fixed_caption(tmp_path, monkeypatch):
    app = subject()
    # Accept both first drafts; replacing the second German sentence requires a new translation.
    answers = iter(
        [
            "Haus",
            "Baum",
            "",
            "",
            "Der Baum wächst im Garten.",
            "",
            "그 나무는 정원에서 자란다.",
        ]
    )
    rendered = []
    original = app.render_card

    def capture(data, word, sentence, translation, date_label):
        rendered.append((sentence, translation))
        return original(data, word, sentence, translation, date_label)

    monkeypatch.setattr(app, "render_card", capture)
    assert (
        app.run(
            root=tmp_path,
            today=date(2026, 9, 19),
            input_fn=lambda prompt: next(answers),
            output_fn=lambda text: None,
            sentence_generator=lambda words: DRAFTS,
            image_generator=lambda prompt: png(),
        )
        == 0
    )
    assert rendered == [
        ("Das Haus ist groß.", "그 집은 크다."),
        ("Der Baum wächst im Garten.", "그 나무는 정원에서 자란다."),
    ]
    folder = tmp_path / "2026-09-19"
    assert (folder / "01_Haus.txt").read_text() == expected_caption()
    assert (folder / "02_Baum.txt").read_text() == expected_caption()


def test_editing_only_translation_keeps_fixed_caption(tmp_path):
    app = subject()
    answers = iter(["Haus", "Baum", "", "그 집은 큽니다.", "", ""])
    assert (
        app.run(
            root=tmp_path,
            input_fn=lambda prompt: next(answers),
            output_fn=lambda text: None,
            sentence_generator=lambda words: DRAFTS,
            image_generator=lambda prompt: png(),
        )
        == 0
    )
    assert all(p.read_text() == expected_caption() for p in tmp_path.rglob("*.txt"))


def test_malformed_model_translation_falls_back_to_manual(tmp_path):
    app = subject()
    answers = iter(MANUAL_INPUT)
    assert (
        app.run(
            root=tmp_path,
            input_fn=lambda prompt: next(answers),
            output_fn=lambda text: None,
            sentence_generator=lambda words: [{"german": "Hallo.", "korean": ""}] * 2,
            image_generator=lambda prompt: png(),
        )
        == 0
    )
    assert all(p.read_text() == expected_caption() for p in tmp_path.rglob("*.txt"))


def test_mcp_failure_preserves_captions_and_reports_partial_result(tmp_path):
    app = subject()
    answers = iter([*MANUAL_INPUT, "", ""])
    output = []

    def failed_image(prompt):
        raise RuntimeError("quota exceeded")

    result = app.run(
        root=tmp_path,
        sentence_generator=unavailable_llm,
        input_fn=lambda prompt: next(answers),
        output_fn=output.append,
        image_generator=failed_image,
    )
    assert result == 1
    assert len(list(tmp_path.rglob("*.txt"))) == 2
    assert not list(tmp_path.rglob("*.jpg"))
    assert any("0/2" in text for text in output)


def test_keyboard_interrupt_is_clean(tmp_path):
    app = subject()

    def cancel(prompt):
        raise KeyboardInterrupt

    assert app.run(root=tmp_path, input_fn=cancel, output_fn=lambda text: None) == 130


def test_blank_and_oversized_input_is_reprompted_in_both_languages(tmp_path):
    app = subject()
    answers = iter(
        [
            "",
            "x" * 81,
            "Haus",
            "Baum",
            "",
            "x" * 401,
            "Das Haus ist groß.",
            "",
            "한" * 401,
            "그 집은 크다.",
            "Der Baum ist grün.",
            "그 나무는 푸르다.",
        ]
    )
    assert (
        app.run(
            root=tmp_path,
            sentence_generator=unavailable_llm,
            input_fn=lambda prompt: next(answers),
            output_fn=lambda text: None,
            image_generator=lambda prompt: png(),
        )
        == 0
    )
    assert len(list(tmp_path.rglob("*.jpg"))) == 2
