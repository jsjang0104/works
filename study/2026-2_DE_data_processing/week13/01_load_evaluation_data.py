"""언어데이터 처리 결과 CSV를 불러오고 기초 정보를 확인합니다.

평가의 출발점: 실제 정답(true_label)과 모델 예측(pred_label)이
같은 표에 있어야 이후 성능 지표·오류 분석을 계산할 수 있습니다.
"""
from pathlib import Path
import pandas as pd

DATA_FILE = Path('evaluation_data.csv')

# 실습이 즉시 실행되도록 CSV가 없으면 예제 데이터를 한 번 생성합니다.
# 열 의미: text=독일어 문장, true_label=정답, pred_label=모델이 예측한 감정 레이블
if not DATA_FILE.exists():
    sample = pd.DataFrame({
        'text': ['Das Buch ist interessant.', 'Der Film war langweilig.', 'Ich liebe diese Musik.',
                 'Das Essen schmeckt nicht.', 'Der Unterricht ist hilfreich.', 'Das Wetter ist schlecht.',
                 'Dieser Roman gefällt mir.', 'Die Aufgabe ist schwierig.', 'Das Konzert war wunderbar.',
                 'Ich bin mit dem Service unzufrieden.'],
        'true_label': ['positive', 'negative', 'positive', 'negative', 'positive', 'negative', 'positive', 'negative', 'positive', 'negative'],
        # 일부 예측은 의도적으로 틀리게 두어 이후 실습에서 오분류를 관찰할 수 있게 합니다.
        'pred_label': ['positive', 'negative', 'positive', 'positive', 'positive', 'negative', 'negative', 'negative', 'positive', 'negative']
    })
    # utf-8-sig: 엑셀에서도 한글·움라우트가 깨지지 않도록 BOM을 붙입니다.
    sample.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')
    print(f'예제 CSV 생성: {DATA_FILE.resolve()}')

df = pd.read_csv(DATA_FILE, encoding='utf-8-sig')

# 평가에 꼭 필요한 열이 빠지면 이후 스크립트가 모두 실패하므로 먼저 검사합니다.
required_columns = {'text', 'true_label', 'pred_label'}
missing = required_columns - set(df.columns)
if missing:
    raise ValueError(f'필수 열이 없습니다: {missing}')

print('=== 데이터 상위 5행 ===')
print(df.head())
print('\n=== 데이터 구조 ===')
print(df.info())  # 행 수, 열 이름, 자료형, 결측 여부를 한눈에 확인
print('\n=== 결측치 개수 ===')
print(df.isnull().sum())  # 비어 있는 값은 지표 계산을 왜곡하므로 반드시 점검
print('\n=== 실제/예측 레이블 분포 ===')
# 교차표: 행=정답, 열=예측. 대각선이 맞힌 수, 바깥이 틀린 수입니다.
print(pd.crosstab(df['true_label'], df['pred_label'], margins=True))
