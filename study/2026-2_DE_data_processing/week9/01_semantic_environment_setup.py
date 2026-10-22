"""01. 의미 분석 실습 환경 준비

이 스크립트는 의미 분석 실습에 필요한 패키지를 설치하는
명령어 목록을 화면에 출력합니다.
실제 설치는 터미널에서 아래 명령어를 직접 실행해야 합니다.
"""

# 실행할 설치/설정 명령어 목록
# (앞에 #이 있는 줄은 예시용으로 비활성화된 명령입니다)
commands = [
    # 가상환경 생성 예시 (필요 시 주석을 해제하고 사용)
    #"python -m venv venv",
    # 가상환경 활성화 예시 (Windows와 macOS/Linux 명령이 다름)
    #"source venv/bin/activate  # Windows: venv\\Scripts\\activate",

    # 의미 분석·시각화에 쓰는 주요 라이브러리 설치
    # - spacy: 형태소/구문/개체명 등 언어 처리
    # - sentence-transformers: 문장 임베딩·유사도
    # - pandas: 표 형태 데이터 처리
    # - matplotlib / seaborn: 그래프·히트맵 시각화
    # - scikit-learn: 유사도·기계학습 유틸
    # - networkx: 의미 네트워크(그래프) 표현
    "pip install spacy sentence-transformers pandas matplotlib seaborn scikit-learn networkx",

    # spaCy 독일어 소형 모델 다운로드
    # (토큰화, POS, NER 등에 사용)
    "python -m spacy download de_core_news_sm",
]

# 학생들이 터미널에 복사해 실행할 수 있도록 명령어를 출력
print("의미 분석 실습 환경 설정 명령:")
for cmd in commands:
    print("-", cmd)
