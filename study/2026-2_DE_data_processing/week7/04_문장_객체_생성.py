# 텍스트를 spaCy에 넣으면 Doc 객체가 생성됩니다.
# Doc는 문장 전체의 분석 결과(토큰, 품사, 의존관계 등)를 담는 컨테이너입니다.

import spacy

nlp = spacy.load("de_core_news_sm")  # 독일어 분석 파이프라인
text = "Die Professorin erklärt den Studierenden die deutsche Syntax sehr geduldig."
doc = nlp(text)  # 텍스트를 분석하여 Doc 객체로 변환

print(type(doc))   # Doc 객체의 타입 확인
print(doc.text)    # Doc에 저장된 원문 텍스트 확인
