# 전치사(ADP)를 찾아 그 하위 트리(subtree)를 합치면 전치사구(PP) 후보가 됩니다.
# token.subtree는 해당 토큰을 중심으로 종속된 모든 토큰을 포함합니다.

import spacy

nlp = spacy.load("de_core_news_sm")
doc = nlp("Der Student arbeitet mit großer Konzentration in der Universitätsbibliothek.")

for token in doc:
    if token.pos_ == "ADP":  # ADP = adposition(전치사/후치사)
        # 전치사와 그에 종속된 토큰들을 공백으로 이어 PP 후보 생성
        subtree = " ".join([t.text for t in token.subtree])
        print({
            "preposition": token.text,   # 전치사 자체
            "pp_candidate": subtree      # 전치사구 전체 후보
        })
