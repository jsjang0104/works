# 같은 문장을 구구조(constituent)와 의존구조(dependency) 관점에서 나란히 비교합니다.
# - 구구조: 어떤 단어들이 하나의 구(NP, PP 등)를 이루는가
# - 의존구조: 각 단어가 어떤 중심어에 어떤 관계로 연결되는가

import spacy

nlp = spacy.load("de_core_news_sm")
doc = nlp("Der Student aus Hamburg liest in der Bibliothek ein spannendes Buch.")

print("[구구조 관점: 명사구 후보]")
for chunk in doc.noun_chunks:
    print(f"- {chunk.text} (중심어: {chunk.root.text})")

print("\n[의존구조 관점: 토큰-중심어 관계]")
for token in doc:
    print(f"- {token.text} -> {token.head.text} ({token.dep_})")
