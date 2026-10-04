# 06_독일어_굴절형과_복합어_사례_해석.py
# 독일어 형태소 분석 실습 6: 독일어 굴절형과 복합어 사례 해석
#
# 이 파일의 목적:
#   - 굴절형(큰/kleinen 등)과 긴 복합어가 어떻게 분석되는지 비교한다.
#   - lemma(표제어)와 morph(형태 자질)를 함께 보면 해석이 쉬움

import spacy

nlp = spacy.load("de_core_news_sm")

# 사례 1~2: 일반 굴절·일치
# 사례 3: 매우 긴 독일어 복합어 (한 토큰으로 남을 수 있음)
texts = [
    "Die Kinder spielen im großen Garten.",
    "Die Studentin liest ein interessantes Buch.",
    "Donaudampfschifffahrtsgesellschaftskapitän ist ein berühmtes Beispiel für ein deutsches Kompositum."
]

for idx, text in enumerate(texts, start=1):
    doc = nlp(text)
    print(f"\n===== 사례 {idx} =====")
    print("문장:", text)
    for token in doc:
        # lemma_: 사전형(기본형). 예: spielen ← spielen의 활용형들
        # morph: Case, Number, Gender 등 굴절 정보
        print(
            f"{token.text:40} | "
            f"lemma={token.lemma_:20} | "
            f"morph={str(token.morph) if token.morph else '-'}"
        )
