import importlib
from datetime import date
from io import BytesIO

from PIL import Image, ImageFont


def subject():
    assert importlib.util.find_spec("cards"), "Implement dated card exports"
    return importlib.import_module("cards")


def test_dated_exports_preserve_german_and_never_overwrite(tmp_path):
    cards = subject()
    first = cards.reserve_output(tmp_path, "../größer", "Der Garten ist größer.", date(2026, 9, 19))
    second = cards.reserve_output(tmp_path, "../größer", "Noch größer.", date(2026, 9, 19))
    assert first.caption.parent == tmp_path / "2026-09-19"
    assert second.caption.parent == first.caption.parent
    assert first.caption != second.caption
    assert "Der Garten ist größer." in first.caption.read_text(encoding="utf-8")
    assert first.image.suffix == ".jpg"
    assert ".." not in first.image.name


def test_existing_orphan_image_is_not_overwritten(tmp_path):
    cards = subject()
    folder = tmp_path / "2026-09-19"
    folder.mkdir()
    (folder / "01_Haus.jpg").write_bytes(b"keep")
    paths = cards.reserve_output(tmp_path, "Haus", "Das Haus ist groß.", date(2026, 9, 19))
    assert paths.image.name != "01_Haus.jpg"
    assert (folder / "01_Haus.jpg").read_bytes() == b"keep"


def test_render_exports_portrait_jpeg_with_original_sentence():
    cards = subject()
    source = BytesIO()
    Image.new("RGB", (768, 1024), "#749e7f").save(source, "PNG")
    rendered = cards.render_card(
        source.getvalue(),
        "zuverlässig",
        "Obwohl es regnet, kommt meine zuverlässige Freundin pünktlich.",
        "비가 오는데도 나의 믿음직한 친구는 제시간에 온다.",
        "2026-09-19",
    )
    image = Image.open(BytesIO(rendered))
    assert image.size == (1080, 1350)
    assert image.format == "JPEG"
    assert image.mode == "RGB"
    assert len(image.getcolors(2_000_000)) > 20


def test_long_compound_words_wrap_without_horizontal_overflow():
    cards = subject()
    font = ImageFont.truetype("DejaVuSans.ttf", 40)
    lines = cards.wrap_text("Donaudampfschifffahrtsgesellschaftskapitän " * 5, font, 280)
    assert len(lines) > 5
    assert all(font.getlength(line) <= 280 for line in lines)
    assert "".join(lines).replace(" ", "") == ("Donaudampfschifffahrtsgesellschaftskapitän" * 5)


def test_caption_contains_only_two_hashtags_and_fixed_body():
    cards = subject()
    assert cards.make_caption() == (
        "#한국외대독일어과 #어휘와구문B2\n\nFLUX Space MCP에 연결하여 AI 이미지를 생성하였습니다.\n"
    )


def test_korean_font_has_distinct_hangul_glyphs():
    import settings

    font = ImageFont.truetype(str(settings.FONT_KOREAN), 36)
    # Unsupported letters would both render as the same missing-glyph box.
    assert bytes(font.getmask("한")) != bytes(font.getmask("글"))


def test_translation_is_below_german_and_date_is_at_top(monkeypatch):
    from PIL import ImageDraw

    cards = subject()
    records = []
    original = ImageDraw.ImageDraw.text

    def capture(self, xy, text, *args, **kwargs):
        records.append(
            (xy, text, self.textbbox(xy, text, font=kwargs["font"], anchor=kwargs.get("anchor")))
        )
        return original(self, xy, text, *args, **kwargs)

    monkeypatch.setattr(ImageDraw.ImageDraw, "text", capture)
    source = BytesIO()
    Image.new("RGB", (500, 500), "white").save(source, "PNG")
    cards.render_card(
        source.getvalue(), "Haus", "Das Haus ist groß.", "그 집은 크다.", "2026-09-19"
    )
    german = next(r for r in records if r[1] == "Das Haus ist groß.")
    korean = next(r for r in records if r[1] == "그 집은 크다.")
    day = next(r for r in records if r[1] == "2026-09-19")
    assert german[2][3] < korean[2][1]
    assert korean[2][3] < 1262
    assert day[2][3] < 100


def test_maximum_length_bilingual_text_stays_inside_card(monkeypatch):
    from PIL import ImageDraw

    cards = subject()
    boxes = []
    original = ImageDraw.ImageDraw.text

    def capture(self, xy, text, *args, **kwargs):
        boxes.append(self.textbbox(xy, text, font=kwargs["font"], anchor=kwargs.get("anchor")))
        return original(self, xy, text, *args, **kwargs)

    monkeypatch.setattr(ImageDraw.ImageDraw, "text", capture)
    source = BytesIO()
    Image.new("RGB", (500, 500), "white").save(source, "PNG")
    cards.render_card(source.getvalue(), "W" * 80, "W" * 400, "한" * 400, "2026-09-19")
    assert all(0 <= x1 < x2 <= 1080 and 0 <= y1 < y2 <= 1350 for x1, y1, x2, y2 in boxes)
    # Every body line remains above the footer divider.
    assert all(y2 < 1262 for x1, y1, x2, y2 in boxes if 700 <= y1 < 1262)
