# 07_각_토큰의_품사_확인.py
# 독일어 품사 태깅 실습 7: 각 토큰의 품사 확인
#
# 이 파일의 목적:
#   - 토큰마다 범용 품사(POS)와 언어별 세분 태그(TAG)를 확인한다.
#   - POS: Universal Dependencies 품사 (NOUN, VERB, ADJ 등) — 언어 간 비교에 유리
#   - TAG: 독일어 세분 태그 (예: NN, VVFIN) — 더 자세한 문법 정보

import spacy

nlp = spacy.load("de_core_news_sm")
text = "Der alte Professor erklärt den Studierenden die linguistischen Modelle."
doc = nlp(text)

print("문장:", text)
print("\n토큰별 품사 정보")

for token in doc:
    # pos_: 범용 품사 라벨 문자열
    # tag_: 모델이 쓰는 세부 품사 태그
    print(f"{token.text:18} | POS={token.pos_:6} | TAG={token.tag_}")
