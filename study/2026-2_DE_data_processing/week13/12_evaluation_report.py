"""평가 결과와 생성된 시각화 파일을 한 번에 요약합니다.

앞 단계 스크립트가 만든 지표와 그림이 있는지 확인하고,
보고서·발표에 넣을 핵심 숫자를 한 표로 모읍니다.
"""
from pathlib import Path
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# 01에서 만든 평가용 CSV를 읽습니다. utf-8-sig는 엑셀에서 한글·움라우트가 깨지지 않게 합니다.
df = pd.read_csv('evaluation_data.csv', encoding='utf-8-sig')
y_true, y_pred = df['true_label'], df['pred_label']

# 02와 같은 가중 평균으로 최종 숫자를 다시 계산해 한 행짜리 요약표를 만듭니다.
summary = pd.DataFrame([{
    'samples': len(df),
    'accuracy': accuracy_score(y_true, y_pred),
    'precision_weighted': precision_score(y_true, y_pred, average='weighted', zero_division=0),
    'recall_weighted': recall_score(y_true, y_pred, average='weighted', zero_division=0),
    'f1_weighted': f1_score(y_true, y_pred, average='weighted', zero_division=0),
    'misclassified_samples': int((y_true != y_pred).sum()),
}])

print('=== 최종 평가 요약 ===')
print(summary.round(3).to_string(index=False))
summary.to_csv('evaluation_summary.csv', index=False, encoding='utf-8-sig')

print('\n=== 생성 여부가 확인된 시각화 파일 ===')
# 09~11번을 먼저 실행해야 아래 PNG가 생깁니다.
for filename in ['performance_bar_chart.png', 'confusion_matrix_heatmap.png', 'error_wordcloud.png']:
    print(f"{'[OK]' if Path(filename).exists() else '[미생성]'} {filename}")

