"""16. 문장 임베딩 유사도

핵심 아이디어:
  표층 유사도(SequenceMatcher)는 글자가 겹치는지만 봅니다.
  임베딩 유사도는 문장을 "의미 공간의 좌표(숫자 목록)"로 바꾼 뒤
  두 좌표가 얼마나 같은 방향을 보는지를 계산합니다.

  임베딩(embedding):
    문장 → 고정 길이 벡터 (예: 384개의 숫자)
    의미가 비슷한 문장은 가까운 좌표를 받습니다.
    글자가 달라도, 뜻이 비슷하면 벡터가 비슷해집니다.

  코사인 유사도:
    cos(a, b) = (a·b) / (|a| × |b|)
    13번·14번과 같은 공식입니다. 벡터만 임베딩으로 바뀝니다.

이 프로그램이 하는 일 (4단계):
  1) 비교할 문장을 준비한다
  2) 문장 임베딩 모델을 불러온다
  3) 각 문장을 벡터로 바꾼다
  4) 코사인 유사도로 문장 쌍이 얼마나 비슷한지 계산한다

입력(texts)만 바꾸면 그대로 쓸 수 있습니다.
점수는 13번·14번·16번(표층)과 같은 [(이름1, 이름2, 점수), ...] 형식입니다.

필요 패키지:
  pip install sentence-transformers
  (01번 환경 설정에 이미 들어 있습니다.)
"""

# math.sqrt: 제곱근. 벡터의 길이(크기)를 구할 때 사용합니다.
from math import sqrt

# SentenceTransformer: 문장을 임베딩 벡터로 바꿔 주는 모델입니다.
# 처음 실행하면 모델을 내려받으므로 시간이 걸릴 수 있습니다.
from sentence_transformers import SentenceTransformer


# =====================================================
# 입력 설정
# 직접 손대는 곳은 여기입니다.
# 이름과 문장만 바꾸면 벡터와 유사도가 자동으로 다시 계산됩니다.
# =====================================================

# 비교할 항목: {이름: 문장}
# 16번 표층 유사도와 같은 문장을 써서, 두 점수를 나란히 비교할 수 있습니다.
texts = {
    "학생-읽기": "Der Student liest ein Buch.",
    "학생-읽기-변형": "Ein Student liest gerade ein Buch.",
    "기차-도착": "Der Zug kommt pünktlich an.",
    "기차-패러프레이즈": "Der Zug erreicht rechtzeitig den Bahnhof.",
    "날씨": "Heute regnet es in Berlin.",
}

# 문장 임베딩 모델 이름
# paraphrase-multilingual-... : 여러 언어(독일어 포함)의 패러프레이즈 비교에 맞춘 모델
# MiniLM-L12-v2               : 비교적 작고 빠른 버전 (벡터 길이 384)
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"


# =====================================================
# 함수들
# 같은 일을 여러 문장에 반복하므로, 미리 절차를 함수로 적어 둡니다.
# =====================================================

def load_embedder(model_name=MODEL_NAME):
    """문장 → 벡터 변환 모델을 불러옵니다.

    처음 한 번은 인터넷에서 모델을 받습니다.
    받은 뒤에는 컴퓨터에 저장되어, 다음부터는 더 빨리 열립니다.
    """
    print(f"모델 불러오는 중: {model_name}")
    print("  (처음이면 내려받기 때문에 잠시 기다릴 수 있습니다.)")
    model = SentenceTransformer(model_name)
    print("  모델을 불러왔습니다.")
    return model


def texts_to_vectors(texts, model):
    """각 문장을 임베딩 벡터(숫자 목록)로 바꿉니다.

    encode():
      문장 여러 개를 한 번에 넣으면, 문장마다 벡터 하나씩 나옵니다.
      모든 벡터의 길이는 같습니다 (이 모델은 보통 384).

    한 번만 변환해 두고, 쌍 비교는 그 벡터로 합니다.
    쌍마다 encode()를 다시 호출하면 같은 문장을 여러 번 변환하게 됩니다.
    """
    names = list(texts.keys())
    sentences = [texts[name] for name in names]

    # convert_to_numpy=True → 각 벡터를 숫자 배열로 받습니다.
    embeddings = model.encode(sentences, convert_to_numpy=True)

    vectors = {}
    for name, embedding in zip(names, embeddings):
        # .tolist(): numpy 배열을 일반 숫자 목록으로 바꿉니다.
        # 13번·14번의 cosine()과 같은 방식으로 계산하기 위해서입니다.
        vectors[name] = embedding.tolist()
    return vectors


def cosine(a, b):
    """두 벡터의 코사인 유사도를 계산합니다.

    공식:  cos(a, b) = (a·b) / (|a| × |b|)

      a·b  : 내적. 같은 위치의 숫자를 곱한 뒤 모두 더함
      |a|  : a의 길이(크기). 각 숫자를 제곱해 더한 뒤 제곱근
      결과 : 보통 -1 ~ 1. 문장 임베딩은 비슷한 의미일수록 1에 가깝습니다.

    13번(Bag-of-Words)·14번(TF-IDF)과 같은 공식입니다.
    다른 점은 벡터를 단어 빈도가 아니라 임베딩으로 만든다는 점뿐입니다.
    """
    # zip: 두 목록에서 같은 위치의 값을 짝지어 꺼냅니다.
    dot = sum(x * y for x, y in zip(a, b))  # 내적
    na = sqrt(sum(x * x for x in a))        # a의 길이
    nb = sqrt(sum(y * y for y in b))        # b의 길이

    # 길이가 0이면 나눌 수 없습니다.
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def pairwise_scores(vectors):
    """모든 항목 쌍의 코사인 유사도를 계산합니다.

    자기 자신과의 비교는 넣지 않습니다 (같은 벡터라 거의 1.0).
    (A, B)만 계산하고 (B, A)는 생략합니다. 같은 점수입니다.

    결과는 [(이름1, 이름2, 점수), ...] 목록입니다.
    18번 Heatmap에 그대로 넣을 수 있는 형식입니다.
    """
    names = list(vectors.keys())
    pairs = []
    for i, name1 in enumerate(names):
        # i+1부터 보면 같은 쌍을 두 번 계산하지 않습니다.
        for name2 in names[i + 1:]:
            score = cosine(vectors[name1], vectors[name2])
            pairs.append((name1, name2, score))
    return pairs


# =====================================================
# 실행 부분: 위에서 만든 함수를 실제로 순서대로 호출합니다.
# =====================================================

print("1) 비교할 문장")
for name, text in texts.items():
    print(f"- {name}")
    print(f"  {text}")
print("-" * 50)


# 2) 모델을 불러 문장마다 임베딩 벡터를 만듭니다.
model = load_embedder(MODEL_NAME)
vectors = texts_to_vectors(texts, model)

print("2) 임베딩 벡터")
print("   각 문장이 같은 길이의 숫자 목록이 됩니다.")
for name, vector in vectors.items():
    preview = [round(x, 3) for x in vector[:6]]  # 앞 6개만 보여 줍니다.
    print(f"- {name}")
    print(f"  문장: {texts[name]}")
    print(f"  벡터 길이: {len(vector)}")
    print(f"  앞부분: {preview} ...")
print("-" * 50)


print("3) 코사인 유사도 (임베딩)")
print("   1에 가까울수록 의미가 비슷하다고 모델이 판단한 것입니다.")
print("   글자가 달라도 뜻이 같으면 표층 유사도보다 높게 나올 수 있습니다.")
scores = pairwise_scores(vectors)
for name1, name2, score in scores:
    print(f"- {name1} - {name2}: {score:.3f}")
print("-" * 50)

# 이 예에서 대략 이렇게 나와야 합니다.
#   학생-읽기 - 학생-읽기-변형 : 높음
#       글자도 비슷하고 의미도 비슷합니다.
#   기차-도착 - 기차-패러프레이즈 : 높음
#       단어는 다르지만 "기차가 제시간에 도착한다"는 의미가 비슷합니다.
#       (16번 표층 유사도는 이 쌍에서 더 낮게 나옵니다.)
#   학생-읽기 - 날씨 : 낮음
#       글자도 의미도 다릅니다.

# 문장을 바꾸고 싶다면 texts만 아래처럼 바꾸면 됩니다.
# texts = {
#     "문장1": "Ich lese ein Buch.",
#     "문장2": "Ich studiere Germanistik.",
#     "문장3": "Das Wetter ist schön.",
# }
