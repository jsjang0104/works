"""가중 Kappa(Weighted Kappa): 순서형 척도에서 '가까운 불일치'를 부분 인정.

예: 점수 1 vs 2는 1 vs 5보다 덜 심각한 불일치입니다.
- linear: 거리 d에 비례해 감점 (1 − d)
- quadratic: 거리 제곱에 비례해 감점 (1 − d²) → 멀리 틀린 경우를 더 엄하게 봄
순서형(리커트 척도, 등급 점수) 주석 신뢰도에 자주 사용합니다.
"""
import numpy as np


def ratio(a, b):
    """나눗셈 도우미. 분모가 0이면 nan을 반환합니다."""
    return float(a / b) if b != 0 else float('nan')


def pairs(a, b):
    """두 평가자 레이블 길이가 같고 비어 있지 않은지 검사한 뒤 배열로 변환합니다."""
    if len(a) != len(b) or not len(a):
        raise ValueError('equal nonzero lengths required')
    return np.asarray(a), np.asarray(b)


def kappa(a, b, categories=None, weight=None):
    """Cohen's kappa / 가중 kappa를 계산합니다. (14번과 동일한 핵심 로직)

    순서형 척도에서는 categories에 전체 등급(예: 1~5)을 빠짐없이 넣는 것이 중요합니다.
    데이터에 안 나온 등급이 빠져 있으면 거리 d가 왜곡될 수 있습니다.
    """
    a, b = pairs(a, b)
    cats = list(categories) if categories is not None else list(dict.fromkeys(list(a) + list(b)))
    if len(cats) < 2:
        return float('nan')
    index = {c: i for i, c in enumerate(cats)}
    if len(index) != len(cats):
        raise ValueError('Duplicate categories')

    # 관측 결합분포(비율)와 기대 결합분포
    obs = np.zeros((len(cats), len(cats)))
    for x, y in zip(a, b):
        obs[index[x], index[y]] += 1
    obs /= len(a)
    exp = np.outer(obs.sum(axis=1), obs.sum(axis=0))

    # 범주 간 정규화 거리 → 가중치 행렬 w
    d = np.abs(np.arange(len(cats))[:, None] - np.arange(len(cats))[None, :]) / (len(cats) - 1)
    if weight is None:
        w = np.eye(len(cats))
    elif weight == 'linear':
        w = 1 - d          # 한 칸 차이면 부분 점수
    elif weight == 'quadratic':
        w = 1 - d ** 2     # 멀리 틀린 불일치를 더 크게 감점
    else:
        raise ValueError('Use None, linear, quadratic')

    po = np.sum(w * obs)
    pe = np.sum(w * exp)
    return ratio(po - pe, 1 - pe)


# 두 평가자가 1~5점 척도로 매긴 점수 (순서형 레이블)
a = [1, 2, 3, 4, 5, 2, 3, 4, 5, 1]
b = [1, 2, 4, 4, 5, 3, 3, 5, 4, 1]

# categories=[1,2,3,4,5]: 데이터에 안 나온 등급이 있어도 전체 척도를 고정합니다.
# (거리 계산이 '실제 점수 간격'을 반영하도록)
for weight in ['linear', 'quadratic']:
    print(f'{weight} weighted kappa = {kappa(a, b, categories=[1, 2, 3, 4, 5], weight=weight):.6f}')
# 보통 quadratic이 linear보다 낮거나 비슷하게 나옵니다(큰 차이를 더 엄하게 보기 때문).
