# 문장의 중심 동사(ROOT)를 찾습니다.
# 의존 트리에서 ROOT는 다른 모든 성분이 직·간접적으로 의존하는 최상위 노드입니다.

import spacy

nlp = spacy.load("de_core_news_sm")
doc = nlp("Die Professorin erklärt den Studierenden die Syntax sehr geduldig.")

# dep_가 "ROOT"인 토큰만 골라냄 (보통 본동사 1개)
root = [token for token in doc if token.dep_ == "ROOT"]
for token in root:
    print("문장 중심 동사:", token.text)
