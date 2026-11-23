"""Cohen's kappa: 우연 일치를 보정한 두 평가자 간 일치도.

κ = (P_o − P_e) / (1 − P_e)
- P_o: 실제로 관측된 일치 비율
- P_e: 레이블 분포만으로 우연히 일치할 것으로 기대되는 비율
κ≈1에 가까울수록 우연 이상으로 잘 일치합니다. (대략 0.6 이상을 양호로 보는 기준도 있음)
"""
import numpy as np


def ratio(a, b):
    """나눗셈 도우미. 분모가 0이면 nan을 반환해 오류 대신 '정의되지 않음'을 표시합니다."""
    return float(a / b) if b != 0 else float('nan')


def pairs(a, b):
    """두 평가자 레이블 길이가 같고 비어 있지 않은지 검사한 뒤 배열로 변환합니다."""
    if len(a) != len(b) or not len(a):
        raise ValueError('equal nonzero lengths required')
    return np.asarray(a), np.asarray(b)


def kappa(a, b, categories=None, weight=None):
    """Cohen's kappa (weight=None) 또는 가중 kappa(linear/quadratic)를 계산합니다.

    categories: 사용할 범주 목록. 순서가 있는 척도에서는 반드시 지정하는 것이 좋습니다.
    weight: None=비가중(완전 일치만), 'linear'/'quadratic'=거리만큼 부분 일치 인정
    """
    a, b = pairs(a, b)
    # 범주가 주어지지 않으면 a,b에 등장한 값을 등장 순서대로 모읍니다.
    cats = list(categories) if categories is not None else list(dict.fromkeys(list(a) + list(b)))
    if len(cats) < 2:
        return float('nan')  # 범주가 하나뿐이면 일치도 논의가 성립하지 않음
    index = {c: i for i, c in enumerate(cats)}
    if len(index) != len(cats):
        raise ValueError('Duplicate categories')

    # obs: 관측된 결합분포(혼동행렬을 비율로 나눈 것). 행=평가자1, 열=평가자2
    obs = np.zeros((len(cats), len(cats)))
    for x, y in zip(a, b):
        obs[index[x], index[y]] += 1
    obs /= len(a)
    # exp: 독립을 가정한 기대 결합분포 = 행주변분포 × 열주변분포
    exp = np.outer(obs.sum(axis=1), obs.sum(axis=0))

    # d: 범주 간 정규화 거리(0=같음, 1=양 끝). 가중치 계산에 사용합니다.
    d = np.abs(np.arange(len(cats))[:, None] - np.arange(len(cats))[None, :]) / (len(cats) - 1)
    if weight is None:
        w = np.eye(len(cats))  # 대각선만 1 → 완전 일치만 인정 (일반 Cohen's kappa)
    elif weight == 'linear':
        w = 1 - d
    elif weight == 'quadratic':
        w = 1 - d ** 2
    else:
        raise ValueError('Use None, linear, quadratic')

    po = np.sum(w * obs)  # 가중 관측 일치
    pe = np.sum(w * exp)  # 가중 기대 일치
    return ratio(po - pe, 1 - pe)


def bootstrap_ci(statistic, rows, repetitions=2000, seed=42):
    """항목(문장)을 복원추출해 통계량의 95% 신뢰구간을 추정합니다.

    평가자(열)는 고정하고, 항목(행)만 다시 뽑아 불확실성을 봅니다.
    표본이 작으면 구간이 넓어질 수 있어 '예시'로만 해석하세요.
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


# 13번과 같은 예제 레이블 (두 평가자의 주석)
a = ['pos', 'pos', 'neg', 'neu', 'neg', 'pos', 'neu', 'neg', 'pos', 'neu']
b = ['pos', 'pos', 'neg', 'pos', 'neg', 'neu', 'neu', 'neg', 'pos', 'neu']
rows = list(zip(a, b))  # 항목별로 (평가자1, 평가자2) 쌍

# weight=None → 일반 Cohen's kappa
stat = lambda r: kappa([x[0] for x in r], [x[1] for x in r])
print(f"Cohen kappa = {stat(rows):.6f}")