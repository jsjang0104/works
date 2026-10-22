"""07. 어휘 의미 분석 시각화

문맥 기반 의미 중의성 해소(예: 04번)에서 얻은
의미 후보 점수를 막대그래프로 시각화합니다.
어느 의미가 더 유력한지 한눈에 비교할 수 있습니다.
"""

import matplotlib.pyplot as plt

# 한글 라벨이 깨지지 않도록 폰트 설정
plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

# 의미 후보별 점수 예시
# (실제로는 04번처럼 키워드 매칭·모델 점수로 계산)
sense_scores = {
    "금융기관": 0.9,  # 높은 점수 → 유력한 의미
    "벤치": 0.2       # 낮은 점수 → 덜 유력
}

plt.figure(figsize=(6, 4))
plt.bar(
    sense_scores.keys(),
    sense_scores.values(),
    color=["#2a9d8f", "#e76f51"]  # 의미별로 다른 색
)

plt.ylim(0, 1)  # 점수 범위 0~1
plt.ylabel("의미 후보 점수")
plt.title("어휘 의미 분석 결과")

plt.tight_layout()
plt.show()
