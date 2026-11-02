"""단층 선형 모델과 은닉층을 가진 다층 신경망 비교

핵심 비교:
- 단층 선형 모델: 데이터를 직선 하나로 나누려고 함
- 다층 신경망: 은닉층을 거쳐 굽은 경계도 그릴 수 있음

초승달 두 개가 맞물린 데이터(moons)는 직선으로 잘 안 나뉩니다.
그래서 신경망이 선형 모델보다 정확도가 높아지는 장면을 볼 수 있습니다.
"""

# make_moons: 초승달 모양 두 덩어리로 된 연습용 분류 데이터
# train_test_split: 학습용/시험용 데이터 분리
# make_pipeline: 전처리와 모델을 한 줄로 이어 붙임
# StandardScaler: 숫자의 평균을 0, 분산을 1로 맞춰 학습이 안정되게 함
# LogisticRegression: 직선(또는 평면)으로 두 클래스를 나누는 선형 분류기
# MLPClassifier: 다층 퍼셉트론, 즉 은닉층이 있는 신경망 분류기
# accuracy_score: 예측이 정답과 얼마나 맞는지 비율로 계산
from sklearn.datasets import make_moons
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score
import numpy as np
import matplotlib.pyplot as plt

# Windows에서 그래프 한글이 깨지지 않도록 글꼴을 지정합니다.
plt.rc("font", family="Malgun Gothic")
# 마이너스 기호(-)가 네모로 깨지는 것을 막습니다.
plt.rc("axes", unicode_minus=False)

# 점 300개를 만들고, noise=0.20으로 살짝 흩뿌려 너무 완벽한 초승달이 되지 않게 합니다.
# X: 각 점의 좌표 (x1, x2)
# y: 그 점이 속한 그룹 (0 또는 1)
X, y = make_moons(n_samples=300, noise=0.20, random_state=42)

# 30%는 시험용으로 남겨, 모델을 "처음 보는 점"으로 평가합니다.
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.3, random_state=42)

# 단층: 입력 → 출력
# 파이프라인 순서: 먼저 스케일 맞추기 → 그다음 로지스틱 회귀로 분류
linear = make_pipeline(StandardScaler(), LogisticRegression())

# 다층: 입력 → 은닉층(뉴런 8개) → 은닉층(뉴런 8개) → 출력
# hidden_layer_sizes=(8, 8): 은닉층이 2개, 각 층에 뉴런 8개
# max_iter=2000: 학습을 최대 2000번 반복 (모자라서 중간에 멈추는 것을 줄임)
mlp = make_pipeline(
    StandardScaler(),
    MLPClassifier(hidden_layer_sizes=(8, 8), max_iter=2000, random_state=42),
)

# 두 모델을 같은 방식으로 학습하고 정확도를 비교합니다.
models = [("단층 선형 모델", linear), ("다층 신경망", mlp)]
for name, model in models:
    model.fit(X_train, y_train)  # 학습 데이터로 규칙을 찾음
    print(name, "정확도:", round(accuracy_score(y_test, model.predict(X_test)), 3))

# 결정 경계 시각화: 격자점마다 모델이 예측한 클래스를 색으로 칠합니다.
# 배경색이 바뀌는 선이 곧 "이 모델이 두 그룹을 나누는 경계"입니다.

# np.linspace: 최솟값~최댓값 사이를 200칸으로 나눈 좌표를 만듭니다.
# meshgrid: 그 좌표로 바둑판처럼 가로·세로 격자점을 만듭니다.
xx, yy = np.meshgrid(
    np.linspace(X[:, 0].min() - 0.5, X[:, 0].max() + 0.5, 200),  # x축 범위
    np.linspace(X[:, 1].min() - 0.5, X[:, 1].max() + 0.5, 200),  # y축 범위
)

# ravel(): 2차원 격자를 1줄로 펼침
# np.c_: x좌표와 y좌표를 짝지어 (점 개수 × 2) 표로 만듦
# 모델은 "점들의 표"를 입력으로 받기 때문에 이 모양이 필요합니다.
grid = np.c_[xx.ravel(), yy.ravel()]

# 그래프를 좌우 2칸 만듭니다. 왼쪽=선형 모델, 오른쪽=신경망
fig, axes = plt.subplots(1, 2, figsize=(10, 4))

for ax, (name, model) in zip(axes, models):
    # 격자 위 모든 점에 대해 0/1을 예측한 뒤, 원래 격자 모양으로 되돌립니다.
    Z = model.predict(grid).reshape(xx.shape)

    # contourf: 예측 결과를 배경색으로 칠해 결정 경계를 보여 줌
    ax.contourf(xx, yy, Z, alpha=0.3, cmap="coolwarm")

    # 실제 데이터 점을 위에 찍음 (색=정답 그룹)
    ax.scatter(X[:, 0], X[:, 1], c=y, cmap="coolwarm", edgecolors="k", s=20)

    ax.set_title(name)
    ax.set_xlabel("x1")
    ax.set_ylabel("x2")

# 두 그래프가 겹치지 않게 여백을 맞춘 뒤 화면에 띄웁니다.
plt.tight_layout()
plt.show()
