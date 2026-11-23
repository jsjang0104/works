"""퍼센트 일치도(Percent Agreement): 두 평가자가 같은 레이블을 준 비율.

주석자 간 신뢰도(inter-annotator agreement)의 가장 단순한 지표입니다.
'우연히 같아질 가능성'은 보정하지 않으므로, 다음 단계(Cohen's kappa)와 함께 봅니다.
"""
import numpy as np


def pairs(a, b):
    """두 평가자 레이블 길이가 같고 비어 있지 않은지 검사한 뒤 배열로 변환합니다."""
    if len(a) != len(b) or not len(a):
        raise ValueError('equal nonzero lengths required')
    return np.asarray(a), np.asarray(b)


def agreement(a, b):
    """일치한 항목 수 / 전체 항목 수 = 0~1 사이 비율을 반환합니다."""
    a, b = pairs(a, b)
    return float(np.mean(a == b))  # True=1, False=0이므로 평균이 곧 일치 비율


# a = 평가자 1, b = 평가자 2의 레이블 (같은 문장/항목에 대한 주석)
# pos=긍정, neg=부정, neu=중립
a = ['pos', 'pos', 'neg', 'neu', 'neg', 'pos', 'neu', 'neg', 'pos', 'neu']
b = ['pos', 'pos', 'neg', 'pos', 'neg', 'neu', 'neu', 'neg', 'pos', 'neu']

# 100을 곱해 %로 출력합니다. (예: 0.8 → 80%)
print(f'Percent agreement = {agreement(a, b) * 100:.4f}%')
# 해석 팁: 값이 높아도 클래스가 한쪽으로 치우치면 '우연히 일치'가 클 수 있습니다.
# 그래서 14번 Cohen's kappa처럼 우연 일치를 보정한 지표를 함께 봅니다.
