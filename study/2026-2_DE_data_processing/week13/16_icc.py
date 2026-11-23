"""ICC(A,1): 급내상관계수 — 여러 평가자의 연속형 점수 일치도.

독일어 작문처럼 0~100점 같은 연속(또는 유사 연속) 점수를
같은 평가자 집합이 매길 때, '절대 합의(absolute agreement)'를 봅니다.
- ICC가 1에 가까울수록 평가자 간 점수가 일관됩니다.
- 이 실습의 ICC(A,1)은 two-way random, absolute agreement, single rater 형태입니다.
"""
import numpy as np


def ratio(a, b):
    """나눗셈 도우미. 분모가 0이면 nan을 반환합니다."""
    return float(a / b) if b != 0 else float('nan')


def icc_a1(ratings):
    """ICC(A,1)을 이원 분산분석(two-way ANOVA) 성분으로 계산합니다.

    ratings: 행=항목(예: 작문), 열=평가자. 결측 없이 숫자만 있어야 합니다.
    MSR: 항목(행) 간 평균제곱 — 항목마다 점수가 얼마나 다른지
    MSC: 평가자(열) 간 평균제곱 — 평가자 편향이 있는지
    MSE: 잔차 평균제곱 — 항목×평가자 상호작용·오차
    """
    x = np.asarray(ratings, dtype=float)
    if x.ndim != 2 or min(x.shape) < 2 or not np.isfinite(x).all():
        raise ValueError('Complete finite matrix, >=2 items and raters required')

    n, k = x.shape          # n=항목 수, k=평가자 수
    grand = x.mean()        # 전체 평균
    row = x.mean(axis=1)    # 항목별 평균
    col = x.mean(axis=0)    # 평가자별 평균

    msr = k * np.sum((row - grand) ** 2) / (n - 1)
    msc = n * np.sum((col - grand) ** 2) / (k - 1)
    mse = np.sum((x - row[:, None] - col[None, :] + grand) ** 2) / ((n - 1) * (k - 1))

    # absolute agreement: 평가자 편향(MSC)도 분모에 넣어 '점수가 같은가'를 엄하게 봅니다.
    return ratio(msr - mse, msr + (k - 1) * mse + k * (msc - mse) / n)


def bootstrap_ci(statistic, rows, repetitions=2000, seed=42):
    """항목(작문)을 복원추출해 ICC의 95% 신뢰구간을 추정합니다.

    평가자는 고정하고 항목만 다시 뽑습니다. 표본이 작으면 구간이 넓어질 수 있습니다.
    """
    rng = np.random.default_rng(seed)
    n = len(rows)
    values = []
    for _ in range(repetitions):
        sample = [rows[i] for i in rng.integers(0, n, n)]
        v = statistic(sample)
        if np.isfinite(v):
            values.append(v)
    if not values:
        return (float('nan'), float('nan'), 0)
    lo, hi = np.quantile(values, [.025, .975])
    return float(lo), float(hi), len(values)


# 독일어 작문 점수(100점 만점): 같은 3명의 평가자가 6편의 글을 모두 채점
# 각 행 = [평가자1, 평가자2, 평가자3]
ratings = [
    [60, 64, 62],
    [65, 69, 68],
    [70, 75, 72],
    [80, 84, 82],
    [85, 89, 87],
    [90, 94, 93],
]

print(f'ICC(A,1), two-way random absolute agreement = {icc_a1(ratings):.6f}')
print('Item-bootstrap 95% CI (fixed raters; illustrative):', bootstrap_ci(icc_a1, ratings))
# 해석: 값이 높으면 평가자들이 비슷한 절대 점수를 준다는 뜻입니다.
# kappa가 '범주 레이블'용인 반면, ICC는 '연속형 점수' 일치도에 적합합니다.
