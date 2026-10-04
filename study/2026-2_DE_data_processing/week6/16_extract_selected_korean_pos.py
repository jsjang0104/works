# 16_한국어_원하는_품사만_추출하기.py
# 한국어 형태소 분석 실습 16: 원하는 품사만 추출하기
#
# 이 파일의 목적:
#   - 전체 형태소 중 관심 품사(여기서는 명사)만 골라낸다.
#   - 키워드 추출·빈도 분석 전처리의 典型적인 패턴
#
# 자주 쓰는 태그 예:
#   NNG: 일반 명사, NNP: 고유 명사
#   VV: 동사, VA: 형용사, JKS/JKO 등: 조사

from kiwipiepy import Kiwi

kiwi = Kiwi()

text = "학생들은 독일 문학 작품을 읽고 언어 데이터를 분석했다."
tokens = kiwi.tokenize(text)

# 일반 명사(NNG), 고유 명사(NNP)만 추출
nouns = [
    token.form
    for token in tokens
    if token.tag in ["NNG", "NNP"]
]

print(nouns)
