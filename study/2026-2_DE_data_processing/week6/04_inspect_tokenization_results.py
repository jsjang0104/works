# 04_토큰_단위_분할_결과_확인.py
# 독일어 형태소 분석 실습 4: 토큰 단위 분할 결과 확인
#
# 이 파일의 목적:
#   - 문장이 어떤 단위(토큰)로 잘리는지 눈으로 확인한다.
#   - 토큰화는 품사·표제어 분석의 출발점이다.

import spacy

nlp = spacy.load("de_core_news_sm")
text = "Die Kinder spielen im großen Garten."
doc = nlp(text)

print("문장:", text)
print("\n토큰 단위 분할 결과")

# enumerate(..., start=1): 번호를 1부터 매기며 토큰을 순회
for i, token in enumerate(doc, start=1):
    # {i:02d}: 번호를 01, 02, ... 형태로 두 자리 표시
    print(f"{i:02d}. {token.text}")
