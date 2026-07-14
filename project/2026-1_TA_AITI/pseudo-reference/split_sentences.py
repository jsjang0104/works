"""
src.txt 의 문장들을 한 줄에 한 문장씩 분리해 out.txt 에 저장합니다.

처리 규칙:
- 원본 텍스트에서 \n 로 분리된 줄은 이미 서로 다른 문장/단락이므로 줄 단위로 먼저 분리.
- 연속된 빈 줄(두 번 이상의 줄바꿈)은 하나의 줄 변경으로 처리하되, 출력에서는 완전히 제거.
- 줄 앞의 들여쓰기(공백/탭)는 제거.
- 줄 내에서 문장 경계(마침표 + 공백 + 대문자)를 감지해 개별 문장으로 분리.
  단, 다음 경우는 문장 경계로 보지 않음:
    - 단일 대문자 이니셜 (예: F. A. Hayek)
    - 공통 약어 (e.g., i.e., etc., U.C.L.A., Ph.D., ...)
    - 괄호 안의 참고문헌 (예: [New York: Oxford University Press, 1968])
    - 번호 목록 (예: 1. 2. 3.)
"""

import re

KEEP_WORD_LIST = {
    "mr",
    "mrs",
    "ms",
    "dr",
    "prof",
    "rev",
    "sr",
    "jr",
    "etc",
    "vs",
    "viz",
    "cf",
    "ibid",
    "et",
    "al",
    "i.e",
    "e.g",
    "op",
    "cit",
    "p",
    "pp",
    "vol",
    "no",
    "ed",
    "eds",
    "fig",
    "est",
    "jan",
    "feb",
    "mar",
    "apr",
    "jun",
    "jul",
    "aug",
    "sep",
    "oct",
    "nov",
    "dec",
    "u.c.l.a",
    "ph.d",
    "b.a",
    "m.a",
    "m.d",
}
_SPLIT_RE = re.compile(r'([.!?]["\')]*)\s+')


def is_boundary(text: str, dot_pos: int) -> bool:
    """dot_pos 위치의 문자가 문장 경계 마침표인지 반환."""
    ch = text[dot_pos]
    if ch in "!?":
        return True  # !? 는 항상 경계

    # ── 마침표 처리 ────────────────────────────────────────────────
    # 앞 단어 추출
    before = text[:dot_pos]
    word_m = re.search(r"[\w.]+$", before)
    if not word_m:
        return True

    word = word_m.group(0)

    # 단일 대문자 이니셜 → 경계 아님 (F. A. Hayek)
    if re.fullmatch(r"[A-Z]", word):
        return False

    # 숫자 → 경계 아님 (1. 2. 연도 등)
    if re.fullmatch(r"\d+", word):
        return False

    # 대문자 약어 (U.S., U.C.L.A.) → 경계 아님
    if re.fullmatch(r"([A-Z]\.)+[A-Z]?", word):
        return False

    # 알려진 약어 → 경계 아님
    if word.lower().rstrip(".") in KEEP_WORD_LIST:
        return False

    return True


def split_sentences(line: str) -> list[str]:
    """한 줄(paragraph) 을 개별 문장 리스트로 분리."""
    line = line.strip()
    if not line:
        return []

    result = []
    start = 0
    for m in _SPLIT_RE.finditer(line):
        if is_boundary(line, m.start()):
            sent = line[start : m.end()].strip()
            if sent:
                result.append(sent)
            start = m.end()

    tail = line[start:].strip()
    if tail:
        result.append(tail)

    return result


def main():
    raw = "raw.txt"
    src = "src.txt"

    with open(raw, encoding="utf-8") as f:
        raw = f.read()

    # 연속 빈 줄 정규화 → 단일 빈 줄
    raw = re.sub(r"\n{2,}", "\n", raw)

    sentences = []
    for line in raw.split("\n"):
        line = line.lstrip()  # 앞 들여쓰기 제거
        if not line:
            continue
        sentences.extend(split_sentences(line))

    with open(src, "w", encoding="utf-8") as f:
        f.write("\n".join(sentences) + "\n")

    print(f"완료: {len(sentences)}개 문장 → {src}")


if __name__ == "__main__":
    main()
