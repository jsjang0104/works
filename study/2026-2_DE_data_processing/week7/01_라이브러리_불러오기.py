# 실습에 필요한 라이브러리를 불러옵니다.

import spacy                 # 자연어처리 라이브러리 (토큰화, 품사, 의존구문분석 등)
from spacy import displacy   # 의존 트리를 HTML로 시각화하는 모듈
from pathlib import Path     # 파일 경로를 다루기 위한 표준 라이브러리

print("spaCy, displaCy, Path 라이브러리 로드 완료")
