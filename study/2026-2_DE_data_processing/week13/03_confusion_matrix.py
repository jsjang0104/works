"""혼동행렬을 생성하고 클래스별 정오분류 수를 해석합니다.

혼동행렬은 '어떤 클래스를 어떤 클래스로 착각했는지'를 표로 보여 줍니다.
숫자 지표만으로는 보이지 않는 오류 패턴을 찾는 출발점입니다.
"""
import pandas as pd
from sklearn.metrics import confusion_matrix

# 01에서 만든 평가용 CSV를 읽습니다. utf-8-sig는 엑셀에서 한글·움라우트가 깨지지 않게 합니다.
df = pd.read_csv('evaluation_data.csv', encoding='utf-8-sig')

# 정답·예측에 등장하는 모든 레이블을 모아 행렬의 행/열 순서를 고정합니다.
# 한쪽 열에만 있는 레이블이 빠져 행렬이 기울어지지 않도록 합집합을 씁니다.
labels = sorted(set(df['true_label']) | set(df['pred_label']))
cm = confusion_matrix(df['true_label'], df['pred_label'], labels=labels)

# 행=실제, 열=예측이 되도록 인덱스를 붙여 읽기 쉽게 만듭니다.
cm_df = pd.DataFrame(cm, index=[f'실제: {x}' for x in labels], columns=[f'예측: {x}' for x in labels])

print('=== 혼동행렬 ===')
print(cm_df)
print('\n행=실제 레이블, 열=예측 레이블입니다. 대각선은 정분류, 비대각선은 오분류입니다.')

# 10번 히트맵·12번 보고서에서 다시 쓸 수 있도록 표로 저장합니다.
cm_df.to_csv('confusion_matrix.csv', encoding='utf-8-sig')
