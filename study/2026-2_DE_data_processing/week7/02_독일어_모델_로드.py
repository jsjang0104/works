# spaCy의 독일어 소형 모델(de_core_news_sm)을 로드합니다.
# 이 모델은 토큰화, 품사 태깅, 의존구문분석 등에 사용됩니다.

import spacy

try:
    # 이미 설치된 독일어 모델을 메모리에 불러옴
    nlp = spacy.load("de_core_news_sm")
    print("독일어 모델 로드 완료")
except OSError:
    # 모델이 없으면 설치 안내를 출력
    print("모델이 설치되어 있지 않습니다.")
    print("터미널에서 다음 명령을 실행하세요:")
    print("python -m spacy download de_core_news_sm")
