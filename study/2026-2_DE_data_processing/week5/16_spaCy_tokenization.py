# ==========================================================
# 독일어 모델 로드 및 기초 토큰화
#
# 12~15번은 규칙(공백, 정규표현식)으로 글을 잘랐습니다.
# 여기서는 spaCy의 독일어 모델이 학습해 둔 지식으로
# 문장 분리와 토큰화를 합니다.
#
# 실행 전에 터미널에서 한 번만 설치하면 됩니다:
#     pip install spacy
#     python -m spacy download de_core_news_sm
#
# 용어 안내:
# - 파이프라인(pipe): 토큰화 → 문장 분리 → 품사 태깅처럼 이어지는 처리 단계
# - 약어(abbreviation): Dr., z.B. 처럼 점(.)이 문장 끝이 아닌 줄임말
# ==========================================================

import spacy
from spacy.language import Language  # 사용자 정의 처리 단계를 등록할 때 사용


# de_core_news_sm: 독일어 소형 모델 (뉴스 텍스트로 학습)
nlp = spacy.load("de_core_news_sm")

# 이 단어들 뒤의 점은 "문장이 끝났다"는 뜻이 아닙니다.
ABBREVIATIONS = {"Dr.", "Prof.", "z.B.", "u.a.", "bzw."}


@Language.component("custom_sentencizer")
def custom_sentencizer(doc):
    """약어 바로 다음 토큰을 새 문장의 시작으로 보지 않게 합니다."""

    # doc[:-1]: 마지막 토큰은 다음 글자가 없으므로 제외합니다.
    for i, token in enumerate(doc[:-1]):
        # 약어 뒤에서는 문장 시작 금지
        # 예: "Dr. Müller"에서 Müller를 새 문장으로 나누지 않습니다.
        if token.text in ABBREVIATIONS:
            doc[i + 1].is_sent_start = False
    return doc


# parser(구문 분석)보다 앞에 넣어, 문장 경계를 먼저 보정합니다.
nlp.add_pipe("custom_sentencizer", before="parser")

text = "Berlin ist die Hauptstadt von Deutschland. Dr. Müller geht heute ins Kino. Das ist z.B. ein wichtiges Thema."

# nlp(text): 모델을 통과시켜 Doc 객체(분석 결과)를 만듭니다.
doc = nlp(text)

print("원문:")
print(f"{text}\n")

print("문장 분리 결과:")
# doc.sents: 모델이 나눈 문장을 하나씩 꺼냅니다.
for sent in doc.sents:
    print(sent.text)

print("\n토큰 정보:")
# doc을 for로 돌리면 토큰(단어·문장부호)이 하나씩 나옵니다.
for token in doc:
    print(f"{token.text}")
