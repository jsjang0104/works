"""Accuracy, Precision, Recall, F1-score를 계산합니다.

- Accuracy(정확도): 전체 중 맞힌 비율
- Precision(정밀도): 모델이 해당 클래스라고 한 것 중 실제로 맞은 비율
- Recall(재현율): 실제 해당 클래스 중 모델이 찾아낸 비율
- F1: 정밀도와 재현율의 조화평균. 한쪽에만 치우친 성능을 보완합니다.
"""
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report

# 01에서 만든 평가용 CSV를 읽습니다. utf-8-sig는 엑셀에서 한글·움라우트가 깨지지 않게 합니다.
df = pd.read_csv('evaluation_data.csv', encoding='utf-8-sig')
# 지표 함수는 '정답 열'과 '예측 열'만 있으면 됩니다.
y_true, y_pred = df['true_label'], df['pred_label']

# average='weighted': 클래스별 지표를 표본 수에 비례해 가중 평균합니다.
#   클래스 불균형이 있을 때 전체 성능을 한 숫자로 요약하는 데 적합합니다.
# zero_division=0: 어떤 클래스를 한 번도 예측하지 않으면 해당 지표를 0으로 두고 경고를 숨깁니다.
metrics = {
    'Accuracy': accuracy_score(y_true, y_pred),
    'Precision (weighted)': precision_score(y_true, y_pred, average='weighted', zero_division=0),
    'Recall (weighted)': recall_score(y_true, y_pred, average='weighted', zero_division=0),
    'F1-score (weighted)': f1_score(y_true, y_pred, average='weighted', zero_division=0),
}

print('=== 분류 성능 지표 ===')
# 소수점 셋째 자리까지 출력해 수업에서 비교하기 쉽게 합니다.
for name, value in metrics.items():
    print(f'{name}: {value:.3f}')

print('\n=== 클래스별 상세 보고서 ===')
# 클래스마다 Precision/Recall/F1과 support(해당 클래스 실제 개수)를 보여 줍니다.
# 전체 평균만 보면 소수 클래스의 실패가 가려질 수 있으므로 반드시 함께 확인합니다.
print(classification_report(y_true, y_pred, zero_division=0))

# 나중에 표·시각화 실습에서 불러 쓸 수 있도록 지표를 CSV로 저장합니다.
pd.DataFrame([metrics]).to_csv('classification_metrics.csv', index=False, encoding='utf-8-sig')
