"""주요 성능 지표를 막대그래프로 시각화합니다.

숫자 표보다 막대그래프가 지표 간 차이를 빠르게 비교하게 해 줍니다.
02에서 계산한 Accuracy/Precision/Recall/F1을 그림으로 저장합니다.
"""
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# 01에서 만든 평가용 CSV를 읽습니다. utf-8-sig는 엑셀에서 한글·움라우트가 깨지지 않게 합니다.
df = pd.read_csv('evaluation_data.csv', encoding='utf-8-sig')
y_true, y_pred = df['true_label'], df['pred_label']

# 02와 같은 가중 평균을 써서 숫자와 그래프가 서로 대응하게 합니다.
metrics = {
    'Accuracy': accuracy_score(y_true, y_pred),
    'Precision': precision_score(y_true, y_pred, average='weighted', zero_division=0),
    'Recall': recall_score(y_true, y_pred, average='weighted', zero_division=0),
    'F1-score': f1_score(y_true, y_pred, average='weighted', zero_division=0),
}

plt.figure(figsize=(8, 5))
bars = plt.bar(metrics.keys(), metrics.values(), color=['#2563EB', '#0EA5E9', '#14B8A6', '#8B5CF6'])
plt.ylim(0, 1.05)  # 분류 지표는 0~1 범위이므로 축을 고정해 비교가 쉽습니다.
plt.ylabel('Score')
plt.title('Classification Performance')
for bar, value in zip(bars, metrics.values()):
    plt.text(bar.get_x() + bar.get_width()/2, value + 0.02, f'{value:.3f}', ha='center')  # 막대 위에 수치 표시
plt.tight_layout()  # 제목·축 레이블이 잘리지 않게 여백을 맞춥니다.
plt.savefig('performance_bar_chart.png', dpi=150)  # 12번 보고서에서 이 PNG 존재 여부를 확인합니다.
plt.show()
