"""독일어 분리동사 자동 인식"""
# 분리동사(예: anfangen)는 활용형이 앞부분(fange)과 전철(an)으로 갈라집니다.
# 의존분석에서 전철은 보통 동사에 의존하며, 라벨은 svp / compound:prt 등으로 표기됩니다.

import spacy

nlp = spacy.load("de_core_news_sm")
text = "Ich fange heute mit der neuen Arbeit an."  # anfangen → fange ... an
doc = nlp(text)

print("전체 토큰 분석:")
for token in doc:
    print(f"{token.text:10} | dep={token.dep_:12} | head={token.head.text:10} | pos={token.pos_}")

print("\n분리동사 후보 탐지:")
for token in doc:
    # svp / compound:prt 라벨이거나, 흔한 분리전철 형태인 경우 후보로 출력
    if token.dep_ == "svp" or token.dep_ == "compound:prt" or token.text.lower() in {"an", "auf", "aus", "ein", "mit", "vor", "zu"}:
        print(f"전철 후보: {token.text} -> head={token.head.text}, dep={token.dep_}")
