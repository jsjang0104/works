"""22. SentiWS 사전 점수로 독일어 문장 감성 판단 (일반화)

핵심 아이디어:
  컴퓨터는 문장의 느낌을 직접 읽지 못합니다.
  그래서 21번과 같이 SentiWS 사전에서 단어 점수를 가져온 뒤,
  그 점수를 더해 문장의 감성을 판단합니다.

  여기에 한 가지를 더합니다.
  독일어 부정어 'nicht'가 수식하는 단어는 점수의 부호를 반전합니다.

  예)
    gut        = +0.3716   → 긍정
    nicht gut  = -0.3716   → 부정  (nicht가 gut를 수식하므로 반전)

  컴퓨터가 점수를 내는 순서:
    1) SentiWS 파일을 읽어 {단어: 점수} 사전을 만든다
    2) spaCy로 문장을 토큰화하고 표제어(lemma)를 구한다
    3) nicht가 가리키는 중심어(head)를 찾아 둔다
    4) 각 토큰 점수를 사전에서 찾고, 부정 대상이면 부호를 뒤집는다
    5) 점수를 더해 문장 총점을 내고, 긍정/부정/중립을 판정한다

이 프로그램이 하는 일 (4단계):
  1) SentiWS 감성 사전을 불러온다
  2) 문장에서 nicht의 수식 대상을 찾는다
  3) 사전 점수와 부정을 반영해 문장 점수를 계산한다
  4) 총점의 부호로 긍정/부정/중립을 출력한다

SENTIWS_DIR과 texts만 바꾸면 그대로 쓸 수 있습니다.
공식 SentiWS(Positive/Negative txt)를 같은 폴더에 넣으면
샘플 대신 실제 사전 점수가 사용됩니다.

필요 패키지:
  pip install spacy
  python -m spacy download de_core_news_sm
  (01번 환경 설정에 이미 들어 있습니다.)
"""

from pathlib import Path

import spacy


# =====================================================
# 입력 설정
# 직접 손대는 곳은 여기입니다.
# 사전 폴더와 문장만 바꾸면 점수가 자동으로 다시 계산됩니다.
# =====================================================

# 이 스크립트가 있는 폴더 기준 경로입니다.
# 터미널을 어디서 실행해도 data/sentiws 를 찾을 수 있습니다.
SCRIPT_DIR = Path(__file__).resolve().parent
SENTIWS_DIR = SCRIPT_DIR / "data" / "sentiws"

# 감성을 판단해 볼 문장들입니다.
# 긍정, nicht 부정, 강한 긍정, 부정 권유, 부정 형용사를 넣었습니다.
# 문장을 더 넣거나 바꿔도, 같은 사전·같은 절차로 점수가 계산됩니다.
texts = [
    "Der Film ist gut.",
    "Der Film ist nicht gut.",
    "Das Ende ist fantastisch.",
    "Nicht zu empfehlen.",
    "Der Film ist langweilig.",
]

# 공식 SentiWS 파일이 아직 없을 때를 위한 샘플입니다.
# 실제 파일과 같은 형식(표제어|품사 / 점수 / 굴절형)으로 적었습니다.
# data/sentiws/*.txt 가 있으면 이 샘플은 쓰이지 않습니다.
SAMPLE_SENTIWS = """
gut|ADJA	0.3716	gute,gutem,guten,guter,gutes
wunderbar|ADJA	0.7234	wunderbare,wunderbarem,wunderbaren,wunderbarer,wunderbares
toll|ADJA	0.5066	tolle,tollem,tollen,toller,tolles
fantastisch|ADJA	0.3319	fantastische,fantastischem,fantastischen,fantastischer,fantastisches
empfehlen|VVINF	0.0040	empfehle,empfiehlst,empfiehlt,empfehlen,empfehlt
schlecht|ADJA	-0.7706	schlechte,schlechtem,schlechten,schlechter,schlechtes
furchtbar|ADJA	-0.3042	furchtbare,furchtbarem,furchtbaren,furchtbarer,furchtbares
langweilig|ADJA	-0.0228	langweilige,langweiligem,langweiligen,langweiliger,langweiliges
"""


# =====================================================
# 함수들
# 같은 일을 여러 줄·여러 문장에 반복하므로, 미리 절차를 함수로 적어 둡니다.
# 사전을 읽는 부분은 21번과 같습니다.
# =====================================================

def parse_sentiws_line(line):
    """SentiWS 한 줄을 읽어 (단어, 점수) 목록으로 바꿉니다.

    예)
      gut|ADJA    0.3716    gute,gutem,guten,guter,gutes

    이 줄에서 나오는 항목:
      ("gut", 0.3716), ("gute", 0.3716), ("gutem", 0.3716), ...

    표제어와 굴절형에 같은 점수를 붙입니다.
    나중에 문장에서 gute 가 나와도, gut 의 점수를 찾을 수 있습니다.
    """
    # strip(): 줄 끝의 공백·줄바꿈을 뗍니다.
    line = line.strip()

    # 빈 줄이나 설명 줄(# 으로 시작)은 건너뜁니다.
    if not line or line.startswith("#"):
        return []

    # split("\t"): 탭을 기준으로 칸을 나눕니다.
    # 칸 0: 표제어|품사
    # 칸 1: 감성 점수
    # 칸 2: 굴절형 (없을 수도 있음)
    parts = line.split("\t")
    if len(parts) < 2:
        return []

    lemma_and_pos = parts[0]          # 예: "gut|ADJA"
    score_text = parts[1]             # 예: "0.3716"
    inflections_text = parts[2] if len(parts) >= 3 else ""

    # "gut|ADJA" → "gut" 만 씁니다. (품사는 이 실습에서 쓰지 않습니다.)
    lemma = lemma_and_pos.split("|")[0].strip()

    try:
        score = float(score_text)
    except ValueError:
        # 점수가 숫자가 아니면 이 줄은 무시합니다.
        return []

    # 표제어를 먼저 넣고, 굴절형이 있으면 뒤에 이어 붙입니다.
    words = [lemma]
    if inflections_text.strip():
        words.extend(inflections_text.split(","))

    entries = []
    for word in words:
        word = word.strip().lower()  # 대소문자 차이를 없앱니다.
        if word:
            entries.append((word, score))
    return entries


def add_entries(lexicon, entries):
    """(단어, 점수) 목록을 사전에 넣습니다.

    같은 단어가 여러 줄에 나오면, 절댓값이 더 큰 점수(더 강한 감성)를 남깁니다.
    예) gut 이 0.20 과 0.37 로 두 번 나오면 0.37 을 사용합니다.
    """
    for word, score in entries:
        old = lexicon.get(word)
        if old is None or abs(score) > abs(old):
            lexicon[word] = score


def read_text_file(path):
    """텍스트 파일을 문자열로 읽습니다.

    SentiWS는 UTF-8인 경우가 많고, 예전 파일은 latin-1 일 수도 있습니다.
    그래서 여러 인코딩을 순서대로 시도합니다.
    """
    for encoding in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError(
        "unknown", b"", 0, 1, f"인코딩을 알 수 없습니다: {path}"
    )


def find_sentiws_files(directory):
    """폴더 안의 SentiWS txt 파일을 찾습니다.

    공식 파일 이름 예:
      SentiWS_v2.0_Positive.txt
      SentiWS_v2.0_Negative.txt
    이 실습의 샘플 파일도 .txt 이므로, 폴더의 txt를 모두 읽습니다.
    """
    directory = Path(directory)
    if not directory.exists():
        return []
    return sorted(path for path in directory.glob("*.txt") if path.is_file())


def load_sentiws(directory=SENTIWS_DIR):
    """SentiWS 파일에서 {단어: 점수} 사전을 만듭니다.

    1) data/sentiws/*.txt 가 있으면 그 파일을 읽습니다.
    2) 파일이 없으면, 위에 적어 둔 SAMPLE_SENTIWS 를 같은 방식으로 읽습니다.

    결과는 예:
      {"gut": 0.3716, "wunderbar": 0.7234, "schlecht": -0.7706, ...}
    """
    lexicon = {}
    files = find_sentiws_files(directory)

    if files:
        source_name = f"파일 {len(files)}개 ({directory})"
        for path in files:
            text = read_text_file(path)
            for line in text.splitlines():
                add_entries(lexicon, parse_sentiws_line(line))
    else:
        source_name = "내장 샘플 (SentiWS 파일이 없어 대체 사용)"
        for line in SAMPLE_SENTIWS.splitlines():
            add_entries(lexicon, parse_sentiws_line(line))

    return lexicon, source_name


def lookup_score(token, lexicon):
    """한 토큰의 감성 점수를 사전에서 찾습니다.

    찾는 순서:
      1) lemma (표제어) 예: guten → gut
      2) 표층형 그대로   예: wunderbar
      3) 둘 다 없으면 0.0 (중립)

    표제어를 먼저 보는 이유:
      문장에는 guten, schlechte 처럼 굴절된 형태가 자주 나옵니다.
      spaCy lemma와 SentiWS 굴절형을 함께 쓰면 더 잘 찾습니다.
    """
    lemma = token.lemma_.lower()
    if lemma in lexicon:
        return lexicon[lemma]

    surface = token.text.lower()
    if surface in lexicon:
        return lexicon[surface]

    return 0.0


def find_negated_targets(doc):
    """nicht가 수식하는 단어의 위치를 모읍니다.

    spaCy에서 token.head 는 그 토큰이 문법적으로 매달린 중심어입니다.
    nicht 의 head 가 바로 '무엇을 부정하는지'에 해당합니다.

    예)
      Der Film ist nicht gut.
      nicht → head = gut   (gut의 점수를 반전)

      Nicht zu empfehlen.
      nicht → head = empfehlen  (empfehlen의 점수를 반전)
    """
    negated_targets = set()
    for token in doc:
        # lemma_.lower(): 대소문자와 굴절을 무시하고 'nicht' 인지만 봅니다.
        if token.lemma_.lower() == "nicht":
            negated_targets.add(token.head.i)
    return negated_targets


def sentence_sentiment(doc, lexicon):
    """문장의 감성 총점과, 점수에 기여한 단어 목록을 계산합니다.

    계산 규칙:
      - 사전에 있는 단어만 점수를 가집니다.
      - nicht가 수식하는 단어는 점수의 부호를 뒤집습니다.
        (gut=+0.37 → nicht gut=-0.37)
      - 문장 총점 = 이렇게 얻은 점수들의 합

    반환값:
      total   : 문장 총점 (실수)
      details : 점수가 0이 아닌 단어들의 설명 목록
    """
    negated_targets = find_negated_targets(doc)

    total = 0.0
    details = []
    for token in doc:
        base = lookup_score(token, lexicon)
        if base == 0.0:
            continue

        # 이 토큰이 nicht의 수식 대상이면 부호를 반전합니다.
        negated = token.i in negated_targets
        used = -base if negated else base
        total += used
        details.append(
            {
                "text": token.text,
                "lemma": token.lemma_,
                "base": base,
                "used": used,
                "negated": negated,
            }
        )
    return total, details


def label_from_score(score):
    """총점의 부호로 긍정/부정/중립을 판정합니다.

    총점 > 0 → 긍정
    총점 < 0 → 부정
    총점 = 0 → 중립 (감성 단어가 없거나, 긍정·부정이 서로 상쇄)
    """
    if score > 0:
        return "긍정"
    if score < 0:
        return "부정"
    return "중립"


# =====================================================
# 실행 부분: 위에서 만든 함수를 실제로 순서대로 호출합니다.
# =====================================================

print("1) SentiWS 감성 사전 불러오기")
LEXICON, source_name = load_sentiws(SENTIWS_DIR)
print(f"   출처: {source_name}")
print(f"   단어 수: {len(LEXICON)}")
print(f"   폴더: {SENTIWS_DIR}")
print("   공식 파일을 쓰려면 Positive/Negative txt를 이 폴더에 넣으면 됩니다.")
print("-" * 50)

# 독일어 모델을 불러옵니다.
# 토큰화와 의존 구문 분석(nicht의 head 찾기)에 사용합니다.
nlp = spacy.load("de_core_news_sm")

print("2) 문장 감성 점수 (nicht 부정 반영)")
print("   사전 점수를 더하되, nicht가 수식하는 단어는 부호를 반전합니다.")
for text in texts:
    doc = nlp(text)
    total, details = sentence_sentiment(doc, LEXICON)
    label = label_from_score(total)

    print(f"\n문장: {text}")
    print(f"  총점: {total:+.4f} → {label}")

    if not details:
        print("  (사전에 있는 감성 단어가 없습니다.)")
        continue

    for item in details:
        # 부정된 단어는 원래 점수와 반전된 점수를 함께 보여 줍니다.
        if item["negated"]:
            note = f"nicht 반영: {item['base']:+.4f} → {item['used']:+.4f}"
        else:
            note = f"score={item['used']:+.4f}"
        print(
            f"  {item['text']:12} "
            f"lemma={item['lemma']:12} "
            f"{note}"
        )
print("-" * 50)

# 이 예에서 대략 이렇게 나와야 합니다.
#   "Der Film ist gut."        → gut 가 양수이므로 긍정
#   "Der Film ist nicht gut."  → gut 의 점수가 반전되어 부정
#   "Das Ende ist fantastisch."→ fantastisch 가 양수이므로 긍정
#   "Nicht zu empfehlen."      → empfehlen 의 점수가 반전되어 부정
#   "Der Film ist langweilig." → langweilig 가 음수이므로 부정

# 문장을 바꾸고 싶다면 texts만 아래처럼 바꾸면 됩니다.
# texts = [
#     "Das Wetter ist toll.",
#     "Das Wetter ist nicht toll.",
#     "Der Abend war furchtbar.",
# ]

# 공식 SentiWS를 쓰려면, 받은 txt 파일을 data/sentiws/ 에 복사하면 됩니다.
# 예) SentiWS_v2.0_Positive.txt , SentiWS_v2.0_Negative.txt
