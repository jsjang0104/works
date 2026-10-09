# spaCy의 noun_chunks로 명사구(NP) 후보를 자동 추출합니다.
# chunk.root는 해당 명사구의 중심어(head noun)입니다.

import spacy

nlp = spacy.load("de_core_news_sm")
doc = nlp("Die Professorin erklärt den motivierten Studierenden die komplizierte Satzstruktur.")

for chunk in doc.noun_chunks:
    print({
        "noun_chunk": chunk.text,      # 명사구 전체 텍스트
        "root": chunk.root.text,       # 명사구의 중심어
        "root_dep": chunk.root.dep_    # 중심어의 의존 관계 라벨 (sb, oa 등)
    })
