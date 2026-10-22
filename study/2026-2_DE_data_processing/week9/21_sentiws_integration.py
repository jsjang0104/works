"""21. SentiWS 감성사전에서 점수를 불러와 토큰에 붙이기 (일반화)

핵심 아이디어:
  SentiWS(SentimentWortschatz)는 독일어 단어마다
  감성 점수(-1 ~ +1)를 적어 둔 사전입니다.

    점수 > 0  → 긍정 단어 (예: wunderbar)
    점수 < 0  → 부정 단어 (예: schlecht)
    점수 = 0  → 사전에 없음, 중립으로 봄

  컴퓨터는 뜻을 직접 읽지 못하므로, 아래 순서로 점수를 붙입니다.
    1) SentiWS 파일을 읽어 {단어: 점수} 사전을 만든다
    2) spaCy로 문장을 토큰화하고 표제어(lemma)를 구한다
    3) 각 토큰의 lemma(없으면 표층형)를 사전에서 찾아 점수를 붙인다
    4) 토큰 점수를 더해 문서 총점을 내고, 긍정/부정/중립을 판정한다

이 프로그램이 하는 일 (4단계):
  1) SentiWS 파일을 불러 감성 사전을 만든다
  2) 각 토큰에 감성 점수를 붙인다
  3) 점수가 있는 토큰을 출력한다
  4) 문장(문서) 총점으로 감성을 판정한다

SENTIWS_DIR에 사전 파일을 두고 texts만 바꾸면 그대로 쓸 수 있습니다.
공식 SentiWS(Positive/Negative txt)를 같은 폴더에 넣으면
샘플 대신 실제 사전 점수가 붙습니다.

SentiWS 한 줄의 모양 (칸은 탭으로 구분):
  gut|ADJA<TAB>0.3716<TAB>gute,gutem,guten,guter,gutes
  ^^^^^^^^     ^^^^^^     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  표제어|품사   감성점수     굴절형들(쉼표로 구분)

필요 패키지:
  pip install spacy
  python -m spacy download de_core_news_sm
  (01번 환경 설정에 이미 들어 있습니다.)
"""

from pathlib import Path

import spacy
from spacy.language import Language
from spacy.tokens import Token


# =====================================================
# 입력 설정
# 직접 손대는 곳은 여기입니다.
# 사전 폴더와 문장만 바꾸면 점수가 자동으로 다시 붙습니다.
# =====================================================

# 이 스크립트가 있는 폴더 기준 경로입니다.
# 터미널을 어디서 실행해도 data/sentiws 를 찾을 수 있습니다.
SCRIPT_DIR = Path(__file__).resolve().parent
SENTIWS_DIR = SCRIPT_DIR / "data" / "sentiws"

# 점수를 붙여 볼 문장들입니다.
# 문장을 더 넣거나 바꿔도, 같은 사전·같은 절차로 점수가 붙습니다.
texts = [
    "Der Film war wunderbar, aber das Ende war schlecht.",
    "Der Film ist gut.",
    "Der Film ist langweilig.",
    "Das Ende ist fantastisch.",
]

# 공식 SentiWS 파일이 아직 없을 때를 위한 샘플입니다.
# 실제 파일과 같은 형식(표제어|품사 / 점수 / 굴절형)으로 적었습니다.
# 파일이 있으면 이 샘플은 쓰이지 않습니다.
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
    # 여기까지 오면 읽기 실패한 것입니다.
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


# 토큰에 사용자 정의 속성(_.sentiws)을 등록합니다.
# 한 번만 등록하면, 이후 token._.sentiws 로 점수를 읽고 쓸 수 있습니다.
if not Token.has_extension("sentiws"):
    Token.set_extension("sentiws", default=0.0)


# spaCy 파이프라인 컴포넌트: 각 토큰에 감성 점수를 붙입니다.
# nlp.add_pipe(...) 로 파이프라인 맨 뒤에 넣으면,
# 토큰화·표제어화가 끝난 뒤에 이 함수가 실행됩니다.
@Language.component("sentiws_component")
def sentiws_component(doc):
    for token in doc:
        token._.sentiws = lookup_score(token, LEXICON)
    return doc


def document_score(doc):
    """문서 총점 = 각 토큰 점수의 합입니다."""
    return sum(token._.sentiws for token in doc)


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

# 독일어 모델을 불러온 뒤, 감성 컴포넌트를 맨 뒤에 추가합니다.
nlp = spacy.load("de_core_news_sm")
nlp.add_pipe("sentiws_component", last=True)

print("2) 토큰별 감성 점수")
print("   lemma 또는 표층형이 사전에 있으면 그 점수를 붙입니다.")
for text in texts:
    doc = nlp(text)
    print(f"\n문장: {text}")
    scored_tokens = [token for token in doc if token._.sentiws != 0]
    if not scored_tokens:
        print("  (사전에 있는 감성 단어가 없습니다.)")
        continue
    for token in scored_tokens:
        print(
            f"  {token.text:12} "
            f"lemma={token.lemma_:12} "
            f"score={token._.sentiws:+.4f}"
        )
print("-" * 50)

print("3) 문서 총점과 감성 판정")
print("   총점 = 토큰 점수의 합. 부호로 긍정/부정/중립을 나눕니다.")
for text in texts:
    doc = nlp(text)
    total = document_score(doc)
    label = label_from_score(total)
    print(f"- {text}")
    print(f"  총점: {total:+.4f} → {label}")
print("-" * 50)

# 이 예에서 대략 이렇게 나와야 합니다.
#   wunderbar  ≈ +0.72, schlecht ≈ -0.77
#   첫 문장은 긍정 단어와 부정 단어가 함께 있어 총점이 0 근처일 수 있습니다.
#   "Der Film ist gut."        → 긍정
#   "Der Film ist langweilig." → 부정

# 문장을 바꾸고 싶다면 texts만 아래처럼 바꾸면 됩니다.
# texts = [
#     "Das Wetter ist toll.",
#     "Der Abend war furchtbar.",
# ]

# 공식 SentiWS를 쓰려면, 받은 txt 파일을 data/sentiws/ 에 복사하면 됩니다.
# 예) SentiWS_v2.0_Positive.txt , SentiWS_v2.0_Negative.txt
