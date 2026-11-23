"""Seaborn heatmap으로 혼동행렬을 시각화합니다.

03의 숫자 표를 색으로 보면 어느 칸에 오류가 몰리는지 한눈에 들어옵니다.
진한 칸일수록 해당 (실제, 예측) 조합이 많다는 뜻입니다.
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix

# 01에서 만든 평가용 CSV를 읽습니다. utf-8-sig는 엑셀에서 한글·움라우트가 깨지지 않게 합니다.
df = pd.read_csv('evaluation_data.csv', encoding='utf-8-sig')
# 03과 같이 정답·예측 레이블의 합집합으로 행/열 순서를 고정합니다.
labels = sorted(set(df['true_label']) | set(df['pred_label']))
cm = confusion_matrix(df['true_label'], df['pred_label'], labels=labels)

plt.figure(figsize=(7, 5))
# annot=True: 칸 안에 건수를 숫자로 표시, fmt='d': 정수 형식
# cmap='Blues': 건수가 많을수록 진하게 보여 대각선(정분류)과 오류 칸을 구분하기 쉽습니다.
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=labels, yticklabels=labels,
            cbar_kws={'label': 'Number of samples'})
plt.xlabel('Predicted label')
plt.ylabel('True label')
plt.title('Confusion Matrix Heatmap')
plt.tight_layout()
plt.savefig('confusion_matrix_heatmap.png', dpi=150)  # 12번 보고서에서 이 PNG 존재 여부를 확인합니다.
plt.show()
