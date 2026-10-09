# 구구조(Konstituentenstruktur) 트리를 HTML 파일로 저장.
# 범위: 동사가 하나인 평서문.
#       명사구(NP), 전치사구(PP), 부사구(AdvP)를 다룰 수 있다.
# 범위 밖: 관계절, weil절처럼 동사가 둘 이상인 문장.

import html
from itertools import product
from pathlib import Path

import spacy
from nltk import CFG
from nltk.parse import ChartParser

# 분석할 문장. 같은 구조의 문장을 이 목록에 추가하면 됩니다.
SENTENCES = [
    # 동사 + 명사구 + 명사구 + 부사구
    "Die Professorin erklärt den Studierenden die deutsche Syntax sehr geduldig.",
    # 동사 + 명사구 + 부사
    "Der Student liest das Buch aufmerksam.",
    # 동사 + 명사구 + 전치사구 (전치사구는 명사구 안에도, 동사구에도 붙을 수 있음)
    "Der Student liest das interessante Buch in der Bibliothek.",
    # 형용사가 들어간 명사구 두 개
    "Die Professorin erklärt den motivierten Studierenden die komplizierte Satzstruktur.",
    # 부사 + 전치사구 + 명사구
    "Der kluge Student liest heute in der Bibliothek ein altes Buch.",
    # 주어 명사구 뒤에 전치사구 (aus Hamburg)
    "Der Student aus Hamburg liest in der Bibliothek ein spannendes Buch.",
    # 주어의 전치사구 + 동사 뒤의 전치사구
    "Die Professorin aus Berlin erklärt den Studierenden die deutsche Syntax mit großer Geduld.",
    # 전치사구 두 개
    "Der Student arbeitet mit großer Konzentration in der Universitätsbibliothek.",
]

# 구 규칙만 적습니다. 단어(Die, Student ...)는 여기 없습니다.
# 격(주격·여격·대격)은 규칙 이름에 넣지 않습니다.
# 같은 NP 규칙으로 세 격을 모두 다루기 위해서입니다.
# Pron은 대명사 하나만으로 된 명사구입니다. 예: er, sie
# #으로 시작하는 줄은 문법 규칙이 아니라 설명입니다. NLTK가 무시합니다.
PHRASE_RULES = """
# 문장 = 명사구 + 동사구 + (마침표)
S -> NP VP PUNCT
S -> NP VP

# 명사구
#   die Syntax                  관사 + 명사
#   die deutsche Syntax         관사 + 형용사 + 명사
#   großer Geduld               형용사 + 명사 (관사가 없을 때)
#   Hamburg                     명사만
#   er                          대명사만
NP -> Det N
NP -> Det Adj N
NP -> Adj N
NP -> N
NP -> Pron

# 명사 뒤에 전치사구가 붙는 명사구
#   der Student aus Hamburg
#   die deutsche Syntax mit großer Geduld
NP -> Det N PP
NP -> Det Adj N PP
NP -> Adj N PP
NP -> N PP

# 전치사구 = 전치사 + 명사구
#   in der Bibliothek
PP -> P NP

# 부사구
#   aufmerksam                  부사 하나
#   sehr geduldig               부사 + 부사
#   sehr langsam                부사 + 형용사 (형용사가 부사처럼 쓰일 때)
AdvP -> Adv
AdvP -> Adv Adv
AdvP -> Adv Adj
"""

# 트리 그림에서 굵게 표시할 구 이름
PHRASAL = {"S", "NP", "VP", "PP", "AdvP"}

# 그림 간격
LEVEL = 74
GAP = 34
MARGIN = 40


def vp_rules(max_after_verb=3):
    """동사 뒤에 오는 성분 규칙을 만듭니다.

    동사 뒤에는 명사구(NP), 전치사구(PP), 부사구(AdvP)가
    최대 max_after_verb개까지, 순서와 상관없이 올 수 있습니다.

    부사구 두 개를 나란히 두는 규칙은 만들지 않습니다.
    'sehr geduldig'는 부사구 두 개가 아니라
    하나의 부사구(Adv + Adv)로 분석되게 하기 위해서입니다.
    """
    rules = ["VP -> V"]
    categories = ["NP", "PP", "AdvP"]
    for length in range(1, max_after_verb + 1):
        for sequence in product(categories, repeat=length):
            adjacent_advp = any(
                sequence[i] == "AdvP" and sequence[i + 1] == "AdvP"
                for i in range(length - 1)
            )
            if adjacent_advp:
                continue
            rules.append("VP -> V " + " ".join(sequence))
    return "\n".join(rules)


def word_category(token):
    """spaCy 품사를 문법 기호로 바꿉니다.

    문법 규칙은 'Det', 'N' 같은 기호만 알고,
    'die'나 'Syntax' 같은 철자는 알지 못합니다.
    그래서 문장을 분석하기 전에 각 단어에 기호를 붙여 줍니다.
    """
    if token.pos_ == "DET":
        return "Det"  # 관사: die, der, das, ein ...
    if token.pos_ in {"NOUN", "PROPN"}:
        return "N"  # 일반명사와 고유명사
    if token.pos_ == "ADJ":
        return "Adj"
    if token.pos_ == "ADV":
        return "Adv"
    if token.pos_ in {"VERB", "AUX"}:
        return "V"
    if token.pos_ == "ADP":
        return "P"  # 전치사: in, mit, aus ...
    if token.pos_ == "PRON":
        return "Pron"
    # 마침표·물음표·느낌표만 문장 끝 부호로 인정합니다.
    # 쉼표는 절이 나뉜다는 뜻이어서 이 문법의 범위 밖입니다.
    if token.pos_ == "PUNCT" and token.text in {".", "?", "!"}:
        return "PUNCT"
    return None


def quote_word(word):
    """NLTK 문법에 넣을 수 있도록 단어를 작은따옴표로 감쌉니다."""
    escaped = word.replace("\\", "\\\\").replace("'", "\\'")
    return f"'{escaped}'"


def build_grammar(doc):
    """구 규칙에 이 문장의 단어 규칙을 이어 붙여 문법을 만듭니다."""
    lexicon = []
    unknown = []
    for token in word_category_pairs(doc):
        category, word = token
        if category is None:
            unknown.append(word)
        else:
            lexicon.append(f"{category} -> {quote_word(word)}")

    if unknown:
        words = ", ".join(unknown)
        raise ValueError(f"이 문법이 다루지 않는 단어가 있습니다: {words}")

    # 구 규칙 + 동사구 규칙 + 이 문장에만 해당하는 단어 규칙
    return CFG.fromstring(PHRASE_RULES + "\n" + vp_rules() + "\n" + "\n".join(lexicon))


def word_category_pairs(doc):
    """(문법 기호, 단어) 목록. 기호를 모르는 단어는 기호가 None입니다."""
    return [(word_category(token), token.text) for token in doc]


def tagged_text(doc):
    """'Die/Det Professorin/N ...' 형식. 품사 기호가 붙었는지 확인하는 용도입니다."""
    parts = []
    for category, word in word_category_pairs(doc):
        parts.append(f"{word}/{category or '?'}")
    return " ".join(parts)


def parse_sentence(nlp, sentence):
    """문장 하나를 분석합니다.

    반환값: (spaCy 문서, 트리 목록, 실패 이유)
    실패한 문장도 건너뛰고 다음 문장을 계속 분석하기 위해 이유를 문자열로 돌려줍니다.
    """
    doc = nlp(sentence)
    try:
        grammar = build_grammar(doc)
    except ValueError as error:
        return doc, [], str(error)

    # ChartParser는 구 규칙에 맞는 트리를 모두 찾습니다.
    # 트리가 둘 이상이면 전치사구가 붙는 위치가 다르다는 뜻인 경우가 많습니다.
    parser = ChartParser(grammar)
    trees = list(parser.parse([token.text for token in doc]))
    if not trees:
        return doc, [], "품사는 확인했지만, 구 규칙에 맞는 구조가 없습니다."
    return doc, trees, ""


# --- 트리 그림 -----------------------------------------------------------
# 1) 각 성분이 가로로 얼마나 넓은지 계산합니다.
# 2) 부모는 자식들의 한가운데에 두고, 단어는 맨 아래 줄에 맞춥니다.
# 3) 부모와 자식을 선으로 잇습니다.
#    부모 바로 다음 높이에 자식을 두면 선이 다른 글자를 가로지르지 않습니다.


def text_width(text, font_px):
    """글자 수로 대략적인 칸 너비를 구합니다."""
    return max(font_px, len(text) * font_px * 0.64 + font_px * 0.5)


def annotate(node):
    """트리 칸의 너비를 아래쪽 단어부터 위로 올라오며 계산합니다."""
    if isinstance(node, str):
        return {"kind": "word", "text": node, "w": text_width(node, 18), "children": []}

    children = [annotate(child) for child in node]
    if children[0]["kind"] == "word":
        content_w = children[0]["w"]
    else:
        content_w = sum(child["w"] for child in children) + GAP * (len(children) - 1)

    return {
        "kind": "node",
        "text": node.label(),
        "w": max(text_width(node.label(), 16), content_w),
        "children": children,
        "phrasal": node.label() in PHRASAL,
    }


def assign_x(box, left):
    """왼쪽 경계를 기준으로 각 칸의 가운데 x 좌표를 정합니다."""
    box["cx"] = left + box["w"] / 2
    children = box["children"]
    if not children:
        return
    if children[0]["kind"] == "word":
        children[0]["cx"] = box["cx"]
        return

    used = sum(child["w"] for child in children) + GAP * (len(children) - 1)
    cursor = left + (box["w"] - used) / 2
    for child in children:
        assign_x(child, cursor)
        cursor += child["w"] + GAP


def assign_depth(box, depth):
    """뿌리(S)를 0으로 해서 부모보다 한 단계 아래에 자식을 둡니다."""
    box["depth"] = depth
    for child in box["children"]:
        assign_depth(child, depth + 1)


def max_depth(box):
    if not box["children"]:
        return box["depth"]
    return max(max_depth(child) for child in box["children"])


def assign_y(box, leaf_depth):
    """구 기호는 깊이대로, 단어만 모두 같은 맨 아래 줄에 둡니다."""
    if box["kind"] == "word":
        box["sy"] = MARGIN + leaf_depth * LEVEL
    else:
        box["sy"] = MARGIN + box["depth"] * LEVEL
    for child in box["children"]:
        assign_y(child, leaf_depth)


def collect(box, lines, labels):
    """그림에 그릴 선과 글자를 모읍니다."""
    css = "word" if box["kind"] == "word" else ("phrasal" if box["phrasal"] else "pos")
    labels.append((box["text"], box["cx"], box["sy"], css))
    for child in box["children"]:
        lines.append((box["cx"], box["sy"] + 13, child["cx"], child["sy"] - 13))
        collect(child, lines, labels)


def render_svg(parse_tree):
    """NLTK 트리 하나를 SVG 그림으로 바꿉니다."""
    root = annotate(parse_tree)
    assign_x(root, MARGIN)
    assign_depth(root, 0)
    leaf_depth = max_depth(root)
    assign_y(root, leaf_depth)

    lines, labels = [], []
    collect(root, lines, labels)

    width = root["w"] + MARGIN * 2
    height = MARGIN + leaf_depth * LEVEL + MARGIN
    line_svg = "\n".join(
        f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" />'
        for x1, y1, x2, y2 in lines
    )
    text_svg = "\n".join(
        f'<text class="{css}" x="{x:.1f}" y="{y:.1f}">{html.escape(text)}</text>'
        for text, x, y, css in labels
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" '
        f'viewBox="0 0 {width:.0f} {height:.0f}">\n{line_svg}\n{text_svg}\n</svg>'
    )


def render_sentence_block(index, sentence, doc, trees, error):
    """문장 하나의 분석 결과를 HTML 덩어리로 만듭니다."""
    parts = [
        '<section class="sentence">',
        f"<h2>{index}. {html.escape(sentence)}</h2>",
        f'<p class="tags">{html.escape(tagged_text(doc))}</p>',
    ]
    if error:
        parts.append(f'<p class="error">{html.escape(error)}</p>')
    else:
        if len(trees) > 1:
            parts.append(
                f"<p class=\"note\">이 문장은 트리가 {len(trees)}개입니다. "
                "전치사구가 앞의 명사구 안에 붙는지, 동사구에 따로 붙는지에 따라 "
                "구조가 달라질 수 있습니다.</p>"
            )
        else:
            parts.append("<p class=\"note\">이 문장은 트리가 1개입니다.</p>")
        for tree_index, tree in enumerate(trees, start=1):
            parts.append(f"<h3>분석 {tree_index}</h3>")
            parts.append(f'<p class="bracket">{html.escape(str(tree))}</p>')
            parts.append(render_svg(tree))
    parts.append("</section>")
    return "\n".join(parts)


def render_page(blocks):
    body = "\n".join(blocks)
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <title>구구조 트리</title>
  <style>
    body {{
      font-family: "Segoe UI", "Malgun Gothic", sans-serif;
      margin: 32px;
      color: #1a1a1a;
      background: #fff;
    }}
    h1 {{ font-size: 22px; font-weight: 650; margin-bottom: 8px; }}
    h2 {{ font-size: 18px; font-weight: 650; margin: 0 0 8px; }}
    h3 {{ font-size: 15px; margin: 18px 0 6px; }}
    .lead, .note {{ font-size: 15px; line-height: 1.7; max-width: 920px; }}
    .sentence {{
      margin: 28px 0 36px;
      padding-top: 8px;
      border-top: 1px solid #ddd;
    }}
    .tags {{
      font-family: Consolas, "Courier New", monospace;
      font-size: 14px;
      line-height: 1.6;
      color: #333;
    }}
    .bracket {{
      font-family: Consolas, "Courier New", monospace;
      font-size: 13px;
      line-height: 1.5;
      color: #333;
      margin: 0 0 12px;
    }}
    .error {{ color: #8a1f1f; }}
    svg {{ max-width: 100%; height: auto; }}
    line {{ stroke: #222; stroke-width: 1.3; }}
    text {{ text-anchor: middle; dominant-baseline: central; fill: #1a1a1a; }}
    .phrasal {{ font-size: 16px; font-weight: 700; }}
    .pos {{ font-size: 15px; }}
    .word {{ font-size: 18px; font-style: italic; }}
    .legend dt {{ font-weight: 650; }}
    .legend dd {{ margin: 0 0 6px 0; }}
  </style>
</head>
<body>
  <h1>구구조 트리 (Konstituentenstruktur)</h1>
  <p class="lead">
    같은 구구조 문법으로 여러 문장을 분석한 결과입니다.
    단어 아래의 Det, N, V 등은 품사 기호이고,
    NP, VP, PP, AdvP는 그 단어들이 이루는 구입니다.
  </p>
  {body}
  <section class="sentence">
    <h2>기호</h2>
    <dl class="legend">
      <dt>S</dt><dd>문장</dd>
      <dt>NP</dt><dd>명사구</dd>
      <dt>VP</dt><dd>동사구</dd>
      <dt>PP</dt><dd>전치사구</dd>
      <dt>AdvP</dt><dd>부사구</dd>
      <dt>Det, Adj, N, V, Adv, P</dt><dd>관사, 형용사, 명사, 동사, 부사, 전치사</dd>
    </dl>
  </section>
</body>
</html>
"""


nlp = spacy.load("de_core_news_sm")
blocks = []
for index, sentence in enumerate(SENTENCES, start=1):
    doc, trees, error = parse_sentence(nlp, sentence)
    # 독일어 문장을 콘솔에 찍으면 Windows 기본 인코딩에서 깨질 수 있어
    # 번호와 트리 개수만 출력합니다. 문장 전문은 HTML에 있습니다.
    if error:
        print(f"[{index}] 분석 실패")
    else:
        print(f"[{index}] 트리 {len(trees)}개")
    blocks.append(render_sentence_block(index, sentence, doc, trees, error))

out_path = Path("constituency_tree.html")
out_path.write_text(render_page(blocks), encoding="utf-8")
print(f"시각화 저장 완료: {out_path.resolve()}")
