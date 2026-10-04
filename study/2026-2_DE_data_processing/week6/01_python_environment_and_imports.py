# 01_Python_환경_및_라이브러리_불러오기.py
# 독일어 형태소 분석 실습 1: Python 환경 및 라이브러리 불러오기
#
# 이 파일의 목적:
#   - 이후 실습에서 쓸 패키지가 설치·로드되는지 확인한다.
#   - 형태소 분석 자체는 다음 파일부터 수행한다.

"""
[사전 준비] 터미널(명령 프롬프트)에서 한 번만 실행하면 됩니다.

1) 패키지 설치
    pip install spacy pandas

2) 독일어 소형 모델 다운로드 (실습 기본)
    python -m spacy download de_core_news_sm

3) (선택) 더 큰 독일어 모델 — 정확도는 높지만 용량·속도 부담이 큼
    python -m spacy download de_core_news_lg

참고:
    - de_core_news_sm / lg 는 spaCy가 제공하는 '독일어' 학습 모델 이름입니다.
    - 모델이 없으면 다음 단계에서 nlp = spacy.load(...) 가 실패합니다.
"""

# spaCy: 토큰화·품사 태깅·표제어 추출 등 NLP 파이프라인을 제공하는 라이브러리
import spacy

# pandas: 분석 결과를 표(DataFrame) 형태로 정리·출력할 때 사용
import pandas as pd

# Counter: 품사·표제어 등의 출현 횟수(빈도)를 셀 때 사용
# (표준 라이브러리이므로 별도 pip 설치 불필요)
from collections import Counter

# 여기까지 오류 없이 실행되면 import가 성공한 것입니다.
print("필수 라이브러리 불러오기가 완료되었습니다.")
print("- spacy: 자연어처리 수행")
print("- pandas: 결과표 정리")
print("- Counter: 빈도 집계")
