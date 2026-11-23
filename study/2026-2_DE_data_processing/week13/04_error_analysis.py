"""오분류 문장을 추출하고 실제→예측 오류 유형을 집계합니다.

지표가 낮을 때 '왜' 틀렸는지를 보려면 틀린 문장 자체를 읽어야 합니다.
오류 유형(예: positive → negative)을 세면 모델이 반복하는 착각을 파악할 수 있습니다.
"""
import pandas as pd

# 01에서 만든 평가용 CSV를 읽습니다. utf-8-sig는 엑셀에서 한글·움라우트가 깨지지 않게 합니다.
df = pd.read_csv('evaluation_data.csv', encoding='utf-8-sig')

# 정답과 예측이 다른 행만 남깁니다. copy()는 이후 열을 추가할 때 원본 df를 건드리지 않기 위함입니다.
errors = df[df['true_label'] != df['pred_label']].copy()
# 예: 'positive → negative'처럼 방향이 보이게 오류 유형을 만듭니다.
errors['error_type'] = errors['true_label'].astype(str) + ' → ' + errors['pred_label'].astype(str)

# 오분류 비율은 Accuracy의 반대편(1 - 정확도)과 같습니다.
print(f'전체 {len(df)}건 중 오분류: {len(errors)}건 ({len(errors)/len(df):.1%})')
print('\n=== 오분류 사례 ===')
# index=False: 행 번호 없이 문장·레이블만 출력해 읽기 쉽게 합니다.
print(errors[['text', 'true_label', 'pred_label', 'error_type']].to_string(index=False))
print('\n=== 오류 유형별 빈도 ===')
print(errors['error_type'].value_counts())  # 어떤 착각이 가장 잦은지 확인

# 11번 단어 빈도·워드클라우드에서 오분류 문장을 다시 쓸 수 있도록 저장합니다.
errors.to_csv('misclassified_data.csv', index=False, encoding='utf-8-sig')
