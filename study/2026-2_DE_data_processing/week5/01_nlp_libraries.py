# ==========================================================
# 독일어 NLP 개발 환경 확인 프로그램
#
# 이 프로그램은 "코드를 실행하기 전에" 실습에 필요한 도구가
# 컴퓨터에 잘 설치되어 있는지 점검합니다.
#
# 기능:
# 1. Python 및 OS 환경 확인
# 2. 설치 라이브러리 버전 확인 (NLP/ML/시각화/유틸리티 포함)
# 3. spaCy 독일어 모델 확인
# 4. Matplotlib 한글 폰트 설정
# 5. CUDA GPU 사용 가능 여부 확인
#
# 용어 안내:
# - 라이브러리: 다른 사람이 만들어 둔 기능을 가져와 쓰는 도구 모음
# - 모듈: import로 불러오는 파이썬 코드 단위
# - 모델: spaCy가 독일어를 분석할 때 사용하는 학습된 데이터
# ==========================================================


# ==========================================================
# 1. 기본 시스템 정보 관련 Import
#    import: 파이썬에 기본으로 들어 있는 기능을 불러옵니다.
# ==========================================================

import sys          # Python 버전, 실행 경로 등 시스템 정보를 볼 때 사용
import platform     # Windows / macOS / Linux 같은 운영체제 정보를 볼 때 사용


# ==========================================================
# 2. 라이브러리 버전 확인 관련 Import
#    (requirements.txt 기준 전체 라이브러리 포함, 없으면 None 처리)
#
#    try / except ImportError 를 쓰는 이유:
#    - 라이브러리가 없어도 프로그램이 중간에 멈추지 않게 하기 위함입니다.
#    - 설치되어 있으면 정상적으로 import 하고,
#      없으면 해당 변수를 None(없음)으로 둡니다.
#    - 나중에 버전을 출력할 때 "설치되지 않음"이라고 알려 줍니다.
# ==========================================================

# NumPy: 숫자 계산, 배열(리스트보다 빠른 숫자 묶음) 처리
try:
    import numpy as np
except ImportError:
    np = None

# Pandas: 표(엑셀처럼 행/열) 형태의 데이터를 다룰 때 사용
try:
    import pandas as pd
except ImportError:
    pd = None

# NLTK: 영어 중심의 자연어처리 도구 (토큰화, 불용어 등)
try:
    import nltk
except ImportError:
    nltk = None

# spaCy: 독일어 형태소 분석, 품사 태깅, 문장 분리 등에 사용
try:
    import spacy
except ImportError:
    spacy = None

# spaCy가 Transformer(BERT 계열) 모델을 쓸 때 필요한 확장 패키지
try:
    import spacy_transformers
except ImportError:
    spacy_transformers = None

# scikit-learn: 머신러닝(분류, 군집 등)에 자주 쓰는 라이브러리
try:
    import sklearn
except ImportError:
    sklearn = None

# PyTorch: 딥러닝 프레임워크. GPU(CUDA) 사용 여부도 여기서 확인합니다.
try:
    import torch
except ImportError:
    torch = None

# Hugging Face Transformers: BERT, GPT 같은 사전학습 언어 모델을 불러올 때 사용
try:
    import transformers
except ImportError:
    transformers = None

# Hugging Face Datasets: 공개 데이터셋을 쉽게 내려받아 쓸 때 사용
try:
    import datasets
except ImportError:
    datasets = None

# Sentence-Transformers: 문장을 숫자 벡터로 바꿔 유사도를 계산할 때 사용
try:
    import sentence_transformers
except ImportError:
    sentence_transformers = None

# Matplotlib: 그래프를 그리는 시각화 라이브러리
# font_manager: 글꼴(한글 폰트)을 지정할 때 사용
try:
    import matplotlib
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
except ImportError:
    matplotlib = None

# Seaborn: Matplotlib을 더 예쁘게 쓰기 쉽게 만든 시각화 라이브러리
try:
    import seaborn as sns
except ImportError:
    sns = None

# WordCloud: 자주 나온 단어를 크기 차이로 보여주는 그림 도구
try:
    import wordcloud
except ImportError:
    wordcloud = None

# NetworkX: 단어 관계, 네트워크 그래프를 그릴 때 사용
try:
    import networkx as nx
except ImportError:
    nx = None

# OpenPyXL: 엑셀(.xlsx) 파일을 읽고 쓸 때 사용
try:
    import openpyxl
except ImportError:
    openpyxl = None

# Requests: 웹페이지 HTML을 받아올 때 사용 (웹크롤링의 첫 단계)
try:
    import requests
except ImportError:
    requests = None

# BeautifulSoup4: HTML 안에서 제목, 본문 같은 원하는 부분만 꺼낼 때 사용
try:
    import bs4
except ImportError:
    bs4 = None

# tqdm: 반복 작업이 얼마나 진행됐는지 진행 막대로 보여 줌
try:
    import tqdm
except ImportError:
    tqdm = None


# ==========================================================
# 3. Python / 운영체제 정보 출력
#    지금 사용 중인 Python 버전이 실습에 맞는지 확인합니다.
# ==========================================================

def print_system_info():
    """현재 컴퓨터의 Python 버전을 출력합니다."""

    print("=" * 60)
    print("Python 정보")
    print("=" * 60)

    # sys.version: Python 버전과 빌드 정보가 들어 있는 문자열
    print(f"Python 버전 : {sys.version}")
    #print(f"Python 실행 파일 : {sys.executable}")

    # 아래는 필요하면 주석을 해제해서 사용할 수 있습니다.
    #print(f"운영체제 : {platform.system()}")
    #print(f"운영체제 버전 : {platform.version()}")
    #print(f"CPU 정보 : {platform.processor()}")

    print()


# ==========================================================
# 4. 설치 라이브러리 버전 출력
#    각 라이브러리가 설치되어 있으면 버전을,
#    없으면 설치 명령어를 알려 줍니다.
# ==========================================================

def print_library_versions():
    """실습에 필요한 라이브러리의 설치 여부와 버전을 출력합니다."""

    print("=" * 60)
    print("설치 라이브러리 버전")
    print("=" * 60)

    # 한 줄이 하나의 라이브러리입니다.
    # (화면에 보여줄 이름, import한 모듈, pip 설치 이름)
    libraries = [
        ("NumPy", np, "numpy"),
        ("Pandas", pd, "pandas"),
        ("NLTK", nltk, "nltk"),
        ("spaCy", spacy, "spacy"),
        ("spacy-transformers", spacy_transformers, "spacy-transformers"),
        ("scikit-learn", sklearn, "scikit-learn"),
        ("PyTorch", torch, "torch"),
        ("Transformers", transformers, "transformers"),
        ("Datasets", datasets, "datasets"),
        ("Sentence-Transformers", sentence_transformers, "sentence-transformers"),
        ("Matplotlib", matplotlib, "matplotlib"),
        ("Seaborn", sns, "seaborn"),
        ("WordCloud", wordcloud, "wordcloud"),
        ("NetworkX", nx, "networkx"),
        ("OpenPyXL", openpyxl, "openpyxl"),
        ("Requests", requests, "requests"),
        ("BeautifulSoup4", bs4, "beautifulsoup4"),
        ("tqdm", tqdm, "tqdm"),
    ]

    # 리스트를 하나씩 꺼내며 설치 여부를 확인합니다.
    for name, module, pip_name in libraries:

        # module이 None이 아니면 → import에 성공 → 설치되어 있음
        if module is not None:
            # getattr: 모듈에 __version__이 있으면 가져오고, 없으면 안내 문구를 씁니다.
            version = getattr(module, "__version__", "버전 정보 없음")
            # :<22 는 이름을 왼쪽 정렬하고 칸을 22칸으로 맞춰 보기 쉽게 합니다.
            print(f"{name:<22}: {version}")
        else:
            # 설치가 안 된 경우, 바로 복사해 실행할 수 있는 pip 명령어를 보여 줍니다.
            print(f"{name:<22}: 설치되지 않음  → pip install {pip_name}")

    print()


# ==========================================================
# 5. 독일어 spaCy 모델 확인
#    spaCy 패키지와 독일어 모델은 별개입니다.
#    spaCy만 설치하고 모델을 안 받으면 독일어 분석이 되지 않습니다.
# ==========================================================

def check_german_model():
    """spaCy 독일어 소형 모델(de_core_news_sm)이 있는지 확인합니다."""

    print("=" * 60)
    print("spaCy 독일어 모델 확인")
    print("=" * 60)

    # de_core_news_sm:
    # de = Deutsch(독일어), core = 기본 모델, news = 뉴스 텍스트로 학습, sm = small(작은 모델)
    model_name = "de_core_news_sm"

    # spaCy 패키지 자체가 없으면 모델을 불러올 수 없습니다.
    if spacy is None:
        print("spaCy가 설치되지 않았습니다.")
        print()
        return  # 이 함수를 여기서 종료하고 다음 검사로 넘어갑니다.

    try:
        # 모델을 실제로 불러와 봅니다. 성공하면 설치되어 있는 것입니다.
        nlp = spacy.load(model_name)

        print(f"✓ {model_name} 설치 완료")
        # nlp.meta는 모델의 버전, 언어 같은 정보가 들어 있는 사전(dict)입니다.
        print(f"  모델 버전 : {nlp.meta.get('version')}")

    except Exception:
        # 모델 파일이 없으면 오류가 나므로, 설치 방법을 안내합니다.
        print(f"✗ {model_name} 설치되지 않음")
        print()
        print("아래 명령어를 실행하여 설치하세요.")
        print()
        print("python -m spacy download de_core_news_sm")

    print()


# ==========================================================
# 6. Windows Matplotlib 한글 폰트 설정
#    그래프에 한글을 쓰면 기본 폰트로는 네모(□)로 깨질 수 있습니다.
#    Windows의 '맑은 고딕'을 지정해 한글이 보이게 합니다.
# ==========================================================

def setup_korean_font():
    """Windows라면 맑은 고딕으로 Matplotlib 한글 표시를 설정합니다."""

    print("=" * 60)
    print("Matplotlib 한글 폰트 설정")
    print("=" * 60)

    # platform.system() 결과 예: "Windows", "Darwin"(macOS), "Linux"
    if platform.system() == "Windows":

        # 맑은 고딕 글꼴 파일 경로 (Windows에 기본 설치되어 있음)
        font_path = r"C:\Windows\Fonts\malgun.ttf"

        # matplotlib와 font_manager가 모두 불러와진 경우에만 설정합니다.
        if matplotlib and font_manager:

            try:
                # 글꼴 파일 경로로 FontProperties 객체를 만듭니다.
                font = font_manager.FontProperties(
                    fname=font_path
                )

                # Matplotlib이 앞으로 사용할 기본 글꼴을 맑은 고딕으로 바꿉니다.
                plt.rcParams["font.family"] = font.get_name()
                # 마이너스(-) 기호가 깨지지 않도록 설정합니다.
                plt.rcParams["axes.unicode_minus"] = False

                print("✓ Windows 맑은 고딕(Malgun Gothic) 설정 완료")

            except Exception:
                print("⚠ 한글 폰트 설정 실패")

        else:
            print("Matplotlib 미설치")

    else:
        print("Windows 환경이 아니므로 기본 폰트 사용")

    print()


# ==========================================================
# 7. CUDA(GPU) 사용 가능 여부 확인
#    CUDA: NVIDIA 그래픽카드로 딥러닝 계산을 빠르게 하는 기술
#    없어도 CPU로 실습은 가능합니다. 다만 속도가 더 느릴 수 있습니다.
# ==========================================================

def check_cuda():
    """PyTorch가 GPU(CUDA)를 쓸 수 있는지 확인합니다."""

    print("=" * 60)
    print("CUDA(GPU) 확인")
    print("=" * 60)

    if torch is None:

        print("PyTorch가 설치되지 않았습니다.")
        print("설치: pip install torch")

    else:

        # True이면 NVIDIA GPU + CUDA 환경이 준비된 상태입니다.
        if torch.cuda.is_available():

            print("✓ CUDA 사용 가능")

            # 컴퓨터에 연결된 GPU가 몇 개인지 확인합니다.
            gpu_count = torch.cuda.device_count()

            print(f"GPU 개수 : {gpu_count}")

            # GPU가 여러 개이면 0번부터 이름을 하나씩 출력합니다.
            for i in range(gpu_count):

                print(
                    f"GPU {i}: "
                    f"{torch.cuda.get_device_name(i)}"
                )

        else:

            print("CUDA 사용 불가능")
            print("CPU 모드로 실행됩니다.")

    print()


# ==========================================================
# 8. 전체 환경 검사 실행
#    위에서 만든 함수들을 순서대로 호출합니다.
#    함수를 나눠 둔 이유: 한 검사가 실패해도 나머지를 계속 진행하기 쉽습니다.
# ==========================================================

def main():
    """환경 검사 전체를 순서대로 실행하는 시작 함수입니다."""

    print()
    print("#" * 60)
    print(" 실습을 위한 라이브러리 설치 여부 검사 ")
    print("#" * 60)
    print()

    print_system_info()         # 1) Python 버전 확인
    print_library_versions()    # 2) 라이브러리 설치/버전 확인
    check_german_model()        # 3) 독일어 spaCy 모델 확인
    setup_korean_font()         # 4) 그래프 한글 폰트 설정
    check_cuda()                # 5) GPU 사용 가능 여부 확인

    print("=" * 60)
    print(" 실습을 위한 라이브러리 설치 여부 검사 완료 ")
    print("=" * 60)


# ==========================================================
# 프로그램 시작점
#
# 이 파일을 직접 실행하면(__name__ == "__main__") main()이 호출됩니다.
# 다른 파일이 이 파일을 import할 때는 main()이 자동 실행되지 않습니다.
# ==========================================================

if __name__ == "__main__":

    main()
