# 토큰과 그 중심어(head) 사이의 거리(토큰 인덱스 차이)를 계산합니다.
# 거리가 크면 장거리 의존 관계일 가능성이 높습니다.
# (예: 관계절이 삽입되어 주어와 동사가 멀리 떨어진 경우)

import spacy

nlp = spacy.load("de_core_news_sm")
# 관계절(das ... gelesen hat)이 삽입된 문장
doc = nlp("Das Buch, das der Student gestern in der Bibliothek gelesen hat, war sehr interessant.")

for token in doc:
    distance = abs(token.i - token.head.i)  # 토큰 위치와 head 위치의 절댓값 거리
    if distance >= 3:  # 거리가 3 이상인 경우만 장거리 의존으로 출력
        print({
            "token": token.text,
            "head": token.head.text,
            "dep": token.dep_,
            "distance": distance
        })
