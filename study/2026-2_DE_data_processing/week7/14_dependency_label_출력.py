# 의존 관계 라벨(dep)과 중심어(head), 품사(pos)를 함께 출력합니다.
# 예: sb(주어), oa(목적어), ROOT(문장 중심) 등

import spacy

nlp = spacy.load("de_core_news_sm")
doc = nlp("Der Student liest das Buch aufmerksam.")

for token in doc:
    print(f"{token.text:12} | dep={token.dep_:12} | head={token.head.text:12} | pos={token.pos_}")
