# 17_문장분리_형태소분석.py
# 한국어 형태소 분석 실습 17: 문장 분리 후 형태소 분석
#
# 이 파일의 목적:
#   - 여러 문장이 섞인 텍스트를 문장 단위로 나눈 뒤,
#     각 문장마다 형태소 분석을 수행한다.
#   - 긴 문서·말뭉치를 다룰 때의 기본 흐름

from kiwipiepy import Kiwi

kiwi = Kiwi()

# 여러 줄·여러 문장이 들어 있는 텍스트
text = """
독일어는 굴절이 발달한 언어이다.
한국어와 독일어의 형태소 구조를 비교해 보자.
자연어처리는 언어 데이터를 계산적으로 분석하는 분야이다.
"""

# split_into_sents: 문장 경계 추정 후 문장 객체 목록 반환
sentences = kiwi.split_into_sents(text)

for i, sentence in enumerate(sentences, start=1):
    # sentence.text: 분리된 한 문장의 문자열
    print(f"\n[문장 {i}] {sentence.text}")

    # 문장별로 tokenize → (형태, 품사) 목록 출력
    tokens = kiwi.tokenize(sentence.text)
    print([(token.form, token.tag) for token in tokens])
