"""German card layout and non-overwriting, date-based exports."""

import os
import re
import tempfile
import unicodedata
from dataclasses import dataclass
from datetime import UTC, date, datetime
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

import settings


@dataclass(frozen=True)
class OutputPaths:
    image: Path
    caption: Path


def make_caption() -> str:
    return (
        "#한국외대독일어과 #어휘와구문B2\n\nFLUX Space MCP에 연결하여 AI 이미지를 생성하였습니다.\n"
    )


def reserve_output(
    root: Path, word: str, caption_text: str, today: date | None = None
) -> OutputPaths:
    """Save the caption first, reserving a unique name for this card."""
    folder = Path(root) / (today or datetime.now(UTC).astimezone().date()).isoformat()
    folder.mkdir(parents=True, exist_ok=True)
    word_slug = re.sub(r"[^\w-]+", "_", unicodedata.normalize("NFC", word))[:40].strip("_-")
    word_slug = word_slug or "wort"
    number = 1
    while True:
        stem = f"{number:02d}_{word_slug}"
        image = folder / f"{stem}.jpg"
        caption = folder / f"{stem}.txt"
        # Sequence numbers are shared by all words and all runs that day.
        if any(folder.glob(f"{number:02d}_*")):
            number += 1
            continue
        try:
            with caption.open("x", encoding="utf-8") as stream:
                stream.write(caption_text)
        except FileExistsError:
            number += 1
            continue
        return OutputPaths(image, caption)


def save_image(path: Path, data: bytes) -> None:
    """Expose only a complete JPEG, and refuse to overwrite an existing file."""
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, suffix=".tmp", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(data)
        os.link(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    lines, current = [], ""
    for word in text.split():
        candidate = f"{current} {word}" if current else word
        if font.getlength(candidate) <= max_width:
            current = candidate
            continue
        if current:
            lines.append(current)
            current = ""
        for letter in word:
            if current and font.getlength(current + letter) > max_width:
                lines.append(current)
                current = ""
            current += letter
    if current:
        lines.append(current)
    return lines


def _fit(
    text: str, *, bold: bool, width: int, height: int, largest: int, smallest: int
) -> tuple[ImageFont.FreeTypeFont, list[str], int]:
    font_path = settings.FONT_BOLD if bold else settings.FONT_REGULAR
    if not Path(font_path).is_file():
        font_path = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    for size in range(largest, smallest - 1, -1):
        font = ImageFont.truetype(font_path, size)
        lines = wrap_text(text, font, width)
        spacing = sum(font.getmetrics()) + 8
        if len(lines) * spacing <= height:
            return font, lines, spacing
    raise ValueError("문장이 카드에 들어가기에는 너무 깁니다. 짧게 수정해 주세요.")


def _bilingual_layout(sentence: str, translation: str, width: int, height: int):
    """Fit both languages together so their blocks cannot overlap."""
    for size in range(43, 14, -1):
        german_font = ImageFont.truetype(settings.FONT_REGULAR, size)
        korean_font = ImageFont.truetype(str(settings.FONT_KOREAN), max(15, round(size * 0.76)))
        korean_font.set_variation_by_name("Regular")
        german_lines = wrap_text(sentence, german_font, width)
        korean_lines = wrap_text(translation, korean_font, width)
        german_step = sum(german_font.getmetrics()) + 6
        korean_step = sum(korean_font.getmetrics()) + 4
        total = len(german_lines) * german_step + 22 + len(korean_lines) * korean_step
        if total <= height:
            return (
                (german_font, german_lines, german_step),
                (korean_font, korean_lines, korean_step),
            )
    raise ValueError("문장과 해석이 카드에 들어가기에는 너무 깁니다. 짧게 수정해 주세요.")


def render_card(
    image_bytes: bytes, word: str, sentence: str, translation: str, date_label: str
) -> bytes:
    canvas = Image.new("RGB", (1080, 1350), "#F6F3EB")
    draw = ImageDraw.Draw(canvas)
    ink, green = "#203B33", "#376854"
    small = ImageFont.truetype(settings.FONT_REGULAR, 22)
    draw.text((64, 49), "WORT & BILD", font=small, fill=green)
    draw.text((1016, 49), date_label, font=small, fill=green, anchor="ra")
    draw.line((64, 91, 1016, 91), fill="#D5DACE", width=2)
    title, lines, step = _fit(word, bold=True, width=952, height=136, largest=68, smallest=22)
    for index, line in enumerate(lines):
        draw.text((64, 114 + index * step), line, font=title, fill=ink, anchor="lt")

    with Image.open(BytesIO(image_bytes)) as original:
        original.load()
        photo = ImageOps.fit(ImageOps.exif_transpose(original).convert("RGB"), (952, 500))
    mask = Image.new("L", photo.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, 951, 499), radius=24, fill=255)
    canvas.paste(photo, (64, 270), mask)
    draw.rounded_rectangle((64, 806, 70, 1236), radius=3, fill="#C56A46")
    german, korean = _bilingual_layout(sentence, translation, width=908, height=430)
    y = 806
    for (font, lines, step), color in ((german, ink), (korean, green)):
        for line in lines:
            draw.text((96, y), line, font=font, fill=color, anchor="lt")
            y += step
        y += 22
    draw.line((64, 1262, 1016, 1262), fill="#D5DACE", width=2)
    draw.text((64, 1286), "DEUTSCH · B1–B2", font=small, fill=green)
    draw.text((1016, 1286), "Wortschatz im Alltag", font=small, fill=green, anchor="ra")
    output = BytesIO()
    canvas.save(output, format="JPEG", quality=95, subsampling=0)
    return output.getvalue()
