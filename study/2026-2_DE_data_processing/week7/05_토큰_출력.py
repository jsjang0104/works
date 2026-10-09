# Doc 객체를 순회하면 각 토큰(단어/구두점)에 접근할 수 있습니다.
# 구조 분석의 가장 기본 단위가 바로 토큰입니다.

import spacy

nlp = spacy.load("de_core_news_sm")
doc = nlp("Der kluge Student liest heute in der Bibliothek ein altes Buch.")

# 문장을 토큰 단위로 하나씩 출력
for token in doc:
    print(token.text)
