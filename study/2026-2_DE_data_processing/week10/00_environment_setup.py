"""NLP 실습 환경 점검: Python 3.10+ 권장

이 파일은 본격적인 실습에 들어가기 전에
필요한 라이브러리가 설치되어 있는지 확인하고,
없으면 자동으로 설치합니다.
"""

# subprocess: 파이썬 코드 안에서 터미널 명령(여기서는 pip install)을 실행할 때 사용
# sys: 지금 실행 중인 파이썬 버전, 파이썬 실행 파일 경로 등을 확인할 때 사용
import subprocess
import sys

# import 이름 -> pip 패키지 이름
# 코드를 쓸 때 쓰는 이름과, 설치할 때 쓰는 이름이 다를 수 있습니다.
# 예: import sklearn  ←→  pip install scikit-learn
packages = {
    "numpy": "numpy",               # 숫자 계산, 벡터/행렬 처리
    "pandas": "pandas",             # 표 형식 데이터 다루기
    "sklearn": "scikit-learn",      # 머신러닝 기본 도구
    "matplotlib": "matplotlib",     # 그래프 그리기
    "seaborn": "seaborn",           # 통계 시각화 (matplotlib 위에 올라가는 도구)
    "torch": "torch",               # 딥러닝 프레임워크 (PyTorch)
    "transformers": "transformers", # BERT 등 사전학습 언어 모델 사용
}

# sys.version은 "3.12.1 (tags/v3.12.1: ...)"처럼 긴 문자열입니다.
# split()[0]으로 앞부분 버전 번호만 잘라 출력합니다.
print(f"Python version: {sys.version.split()[0]}")

# 아직 설치되지 않은 패키지 이름을 모아 둘 빈 리스트
missing = []

# packages 딕셔너리를 하나씩 꺼내며 설치 여부를 확인합니다.
# import_name: import할 때 쓰는 이름
# pip_name: pip install할 때 쓰는 이름
for import_name, pip_name in packages.items():
    try:
        # __import__("numpy")는 import numpy와 비슷한 일을 합니다.
        # 문자열이므로 반복문 안에서 동적으로 모듈을 불러올 수 있습니다.
        module = __import__(import_name)
        # 대부분 라이브러리는 __version__에 버전 번호를 가지고 있습니다.
        # 없으면 'installed'라고만 표시합니다.
        print(f"[OK] {import_name}: {getattr(module, '__version__', 'installed')}")
    except ImportError:
        # import가 실패하면 그 모듈이 아직 설치되지 않은 것입니다.
        print(f"[MISSING] {import_name}")
        missing.append(pip_name)

if missing:
    # 빠진 패키지가 있으면, 설치 명령을 보여주고 바로 실행합니다.
    print(f"\n미설치 모듈만 설치: pip install {' '.join(missing)}")
    # sys.executable: 지금 이 코드를 실행 중인 파이썬 경로
    # -m pip: 그 파이썬에 딸린 pip을 사용 (다른 파이썬에 설치되는 실수를 막음)
    subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])
else:
    print("\n모든 모듈이 설치되어 있습니다.")
