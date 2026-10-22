"""02. 시각화를 위한 Python 실습 환경

의미 분석 결과를 그래프로 그릴 때 필요한
한글 폰트·Seaborn 테마 설정을 점검하는 스크립트입니다.
막대그래프가 깨지지 않고 나오면 환경이 준비된 것입니다.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib import font_manager
import seaborn as sns
import os

# =====================================================
# Windows 한글 폰트 설정
# (그래프 제목·축 라벨의 한글이 깨지지 않게 함)
# =====================================================
font_path = r"C:\Windows\Fonts\malgun.ttf"  # 맑은 고딕

# 폰트 파일이 없으면 이후 그래프에서 한글이 깨지므로 바로 중단
if not os.path.exists(font_path):
    raise FileNotFoundError(f"폰트를 찾을 수 없습니다.\n{font_path}")

# matplotlib에 폰트를 등록하고 실제 폰트 이름을 가져옴
font_manager.fontManager.addfont(font_path)
font_name = font_manager.FontProperties(fname=font_path).get_name()

# Seaborn 기본 테마(흰 배경 + 격자)
sns.set_theme(style="whitegrid")

# Matplotlib 전역 폰트 설정
mpl.rcParams["font.family"] = font_name
mpl.rcParams["font.sans-serif"] = [font_name]
# 마이너스 기호가 네모로 깨지는 현상 방지
mpl.rcParams["axes.unicode_minus"] = False

# =====================================================
# 점검용 예시 데이터 (유사도 점수 0~1)
# =====================================================
values = np.array([0.25, 0.60, 0.85])
labels = ["낮은 유사도", "중간 유사도", "높은 유사도"]

# =====================================================
# 막대그래프로 환경이 정상인지 확인
# =====================================================
fig, ax = plt.subplots(figsize=(6, 4))

ax.bar(
    labels,
    values,
    color=["#8ecae6", "#219ebc", "#023047"]  # 낮음→높음 색 그라데이션
)

ax.set_title("의미 분석 시각화 환경 점검", fontsize=15)
ax.set_ylabel("점수", fontsize=12)
ax.set_ylim(0, 1)  # 유사도 점수 범위에 맞춤

plt.tight_layout()
plt.show()
