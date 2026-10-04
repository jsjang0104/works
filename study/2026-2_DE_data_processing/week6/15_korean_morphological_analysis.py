# 15_한국어_형태소_분석.py
# 한국어 형태소 분석 실습 15: Kiwi로 한국어 형태소 분석하기
#
# 이 파일의 목적:
#   - 독일어(spaCy)와 달리, 한국어는 Kiwi(kiwipiepy)로 형태소 단위를 본다.
#   - 출력: (형태, 품사태그) 쌍의 목록
#
# 사전 준비 (터미널):
#   pip install kiwipiepy

from kiwipiepy import Kiwi

# 형태소 분석기 객체 생성 (한 번 만들어 두고 재사용)
kiwi = Kiwi()

text = "독일어 형태소 분석과 자연어처리 수업을 진행합니다."

# kiwi.tokenize(text): 문장을 형태소 단위로 분석
# token.form: 형태소 문자열, token.tag: 품사 태그 (NNG, JKB, VV 등)
morphemes = [
    (token.form, token.tag)
    for token in kiwi.tokenize(text)
]

print(morphemes)
