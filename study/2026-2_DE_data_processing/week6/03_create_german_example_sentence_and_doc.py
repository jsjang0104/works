# 03_독일어_예제문장_입력_및_분석객체_생성.py
# 독일어 형태소 분석 실습 3: 독일어 예제 문장 입력 및 분석 객체 생성
#
# 이 파일의 목적:
#   - 문자열(text)을 spaCy에 넣어 Doc 객체를 만든다.
#   - Doc은 토큰·품사·표제어 등 분석 결과가 들어 있는 컨테이너이다.

import spacy

nlp = spacy.load("de_core_news_sm")

# 분석할 독일어 예제 문장 (필요하면 바꿔 실습해도 됨)
text = "Die Studierenden lesen wissenschaftliche Artikel und analysieren Sprachverarbeitungsmodelle an der Universität."

# nlp(text): 파이프라인 실행 → Doc 객체 생성
# Doc 안에는 토큰(token)들이 순서대로 들어 있음
doc = nlp(text)

print("입력 문장:")
print(text)
print("\n분석 객체 생성 완료")
print("토큰 수:", len(doc))  # Doc의 길이 = 토큰 개수
# token.text: 원문에 나타난 그대로의 토큰 문자열
print("토큰 목록:", [token.text for token in doc])
