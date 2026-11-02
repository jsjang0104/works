"""작은 표 데이터로 분류 규칙을 학습하는 머신러닝 실습

아이디어:
- 사람처럼 "꽃잎이 길면 A종"이라고 규칙을 직접 쓰지 않습니다.
- 컴퓨터가 이미 정답이 있는 데이터를 보고, 스스로 규칙을 찾습니다.
- 이 실습에서는 그 규칙이 사람 눈에 보이는 결정 트리(Decision Tree)를 사용합니다.
"""

# load_iris: 꽃 품종 분류에 자주 쓰이는 연습용 데이터셋
# train_test_split: 데이터를 학습용과 시험용으로 나눔
# DecisionTreeClassifier: 질문(예: 꽃잎 길이가 2.5보다 긴가?)을 이어가며 분류하는 모델
# export_text: 학습된 트리를 글자로 보여 줌
# accuracy_score: 정답과 예측이 얼마나 일치하는지 계산
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.metrics import accuracy_score

# 1) 표 형식 데이터 읽기
# as_frame=True이면 pandas DataFrame(엑셀 표와 비슷한 형태)으로 받습니다.
iris = load_iris(as_frame=True)

# X: 모델이 보고 판단하는 입력 특징(feature)
#    꽃받침 길이/너비, 꽃잎 길이/너비 4가지 숫자
X = iris.data

# y: 사람이 미리 붙여 둔 정답 라벨(target)
#    꽃 종류를 숫자 0, 1, 2로 표시 (setosa, versicolor, virginica)
y = iris.target

# 데이터가 어떤 표인지 초보자가 바로 볼 수 있게 일부만 미리 보여 줍니다.
# shape: (행 개수, 열 개수) → 꽃 150송이, 측정값 4가지
print("데이터 크기:", X.shape)
print("열 이름:", list(X.columns))
print("품종 이름:", iris.target_names.tolist())  # 0=setosa, 1=versicolor, 2=virginica

# 특징(X)과 정답(y)을 한 표로 붙여 앞 5행만 출력합니다.
preview = X.copy()
preview["품종번호"] = y
preview["품종이름"] = iris.target_names[y]
print("\n데이터 미리보기 (앞 5행):")
print(preview.head().to_string())  # to_string(): 열이 잘리지 않고 전부 보이게 함
print()

# 2) 학습용/평가용 데이터 분리
# 시험 문제를 미리 보여 주면 답을 외울 수 있듯이,
# 머신러닝도 "본 적 없는 데이터"로 실력을 재야 합니다.
# 그래서 데이터를 두 덩어리로 나눕니다.
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.25,     # 전체의 25%를 시험용으로 남겨 둠
    random_state=42,    # 난수를 고정해서 실행할 때마다 같은 분할이 나오게 함
    stratify=y,         # 꽃 종류 비율이 학습/시험 세트에서 비슷하게 유지되도록 함
)

# 3) 분류기 학습과 예측
# max_depth=3: 질문을 너무 많이 이어가면 학습 데이터만 외우게 됩니다(과적합).
#              깊이 3으로 제한해 단순한 규칙을 만들게 합니다.
model = DecisionTreeClassifier(max_depth=3, random_state=42)

# fit: 학습 데이터를 보고 분류 규칙을 찾는 단계
model.fit(X_train, y_train)

# predict: 시험 데이터의 꽃 종류를 규칙에 따라 맞춰 봄
pred = model.predict(X_test)

# 정확도 = (맞힌 개수) / (전체 시험 개수)
print("정확도:", round(accuracy_score(y_test, pred), 3))

# 숫자 라벨(0, 1, 2) 대신 실제 품종 이름으로 앞 5개 예측을 보여 줍니다.
print("첫 5개 예측:", iris.target_names[pred[:5]])

# 4) 학습된 규칙 확인
# 아래 줄의 #을 지우면, 모델이 만든 "if 꽃잎 길이 > ... then ..." 규칙을
# 텍스트로 볼 수 있습니다.
#print(export_text(model, feature_names=list(X.columns)))
