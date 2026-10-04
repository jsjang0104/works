# 12_표제어_추출_결과의_활용_해석.py
# 독일어 표제어 추출 실습 12: 표제어 추출 결과의 활용 해석
#
# 이 파일의 목적:
#   - 내용어 표제어를 모아 "핵심 어휘 목록"을 만든다.
#   - 집합(set)으로 중복을 제거하고, 정렬해 읽기 쉽게 출력한다.

import spacy

nlp = spacy.load("de_core_news_sm")
text = "Die Kinder gingen in die Bibliotheken, lasen Bücher und waren sehr glücklich."
doc = nlp(text)

# 집합 내포: 내용어 lemma만 모아 소문자로 통일 → 중복 제거 → sorted로 정렬
lemmas = sorted({
    token.lemma_.lower()
    for token in doc
        if token.pos_ in {"VERB", "NOUN", "ADJ"}
})

print("핵심 표제어 목록")
print(lemmas)
print("\n활용 해석")
print("- 다양한 굴절형을 하나의 기본형으로 통합할 수 있다.")
print("- 핵심 어휘 목록을 구축할 수 있다.")
print("- 검색, 빈도 분석, 말뭉치 분석의 전처리 자료로 활용할 수 있다.")
