"""06. 개체명 인식(NER) 추출

spaCy 독일어 모델로 문장에서
사람(PER), 장소(LOC), 날짜(DATE) 등
고유한 개체(Named Entity)를 찾아 라벨과 함께 출력합니다.
"""

import spacy

# 독일어 소형 모델 로드 (01에서 다운로드한 de_core_news_sm)
nlp = spacy.load("de_core_news_sm")

# NER 대상 예문: 인명, 지명, 날짜가 포함됨
text = "Angela Merkel hat in Berlin am 3. Oktober die Universität besucht."
doc = nlp(text)

print("개체명 인식 결과:")
# doc.ents: 모델이 인식한 개체명 목록
for ent in doc.ents:
    # ent.text = 표면형, ent.label_ = 개체 유형(PER, LOC, DATE 등)
    print(f"- {ent.text:20} | label={ent.label_}")
