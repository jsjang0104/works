# 명사구(NP)와 전치사구(PP) 후보를 함께 정리해 구구조 관점을 확인합니다.

import spacy

nlp = spacy.load("de_core_news_sm")
doc = nlp("Die Professorin aus Berlin erklärt den Studierenden die deutsche Syntax mit großer Geduld.")

print("[구구조 후보 정리]")

# 1) 명사구 후보와 그 중심어
for chunk in doc.noun_chunks:
    print(f"NP 후보: {chunk.text} | 중심어: {chunk.root.text}")

# 2) 전치사(ADP)의 subtree로 전치사구 후보 추출
for token in doc:
    if token.pos_ == "ADP":
        phrase = " ".join([t.text for t in token.subtree])
        print(f"PP 후보: {phrase} | 중심어: {token.text}")
