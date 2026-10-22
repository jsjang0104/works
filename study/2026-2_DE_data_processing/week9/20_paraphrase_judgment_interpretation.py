"""20. 패러프레이즈 판단을 위한 의미 유사도 점수 (일반화)

핵심 아이디어:
  패러프레이즈(paraphrase)는 단어·어순은 달라도
  핵심 사건 의미가 비슷한 문장 쌍입니다.

  컴퓨터는 뜻을 직접 읽지 못하므로, 아래 순서로 점수를 냅니다.
    1) 각 문장을 임베딩 벡터(숫자 목록)로 바꾼다
    2) 두 벡터의 코사인 유사도를 계산한다  → 의미 유사도 점수
    3) 점수가 임계값(threshold) 이상이면 패러프레이즈로 판정한다

  표층 유사도(16번)는 글자가 겹치는지만 봅니다.
  여기서 쓰는 점수는 17번과 같은 임베딩 코사인 유사도입니다.
  글자가 달라도 뜻이 비슷하면 높게 나올 수 있습니다.

이 프로그램이 하는 일 (5단계):
  1) 비교할 문장 쌍을 준비한다
  2) 문장 임베딩 모델을 불러온다
  3) 등장하는 문장을 한 번씩만 벡터로 바꾼다
  4) 쌍마다 의미 유사도 점수를 계산한다
  5) 임계값과 비교해 패러프레이즈 여부를 판정하고 짧게 해석한다

입력(pairs)과 임계값(threshold)만 바꾸면 그대로 쓸 수 있습니다.
점수는 20번 원래 형식인 [(문장1, 문장2, 점수), ...] 로도 남깁니다.

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
# 문장 쌍과 임계값만 바꾸면 점수와 판정이 자동으로 다시 계산됩니다.
# =====================================================

# 비교할 문장 쌍: (이름, 문장1, 문장2)
#   이름   : 결과를 알아볼 때 쓰는 짧은 표지
#   문장1·2: 실제로 의미가 비슷한지 볼 두 문장
#
# 19번의 패러프레이즈 예와, 의미가 다른 대조 예를 함께 넣었습니다.
pairs = [
    (
        "기차-도착",
        "Der Zug kommt pünktlich an.",
        "Der Zug erreicht rechtzeitig den Bahnhof.",
    ),
    (
        "강의-시작",
        "Die Vorlesung beginnt um neun Uhr.",
        "Um neun Uhr startet die Vorlesung.",
    ),
    (
        "책-비행",
        "Ich lese ein Buch.",
        "Morgen fliege ich nach Wien.",
    ),
]

# 이 점수 이상이면 패러프레이즈로 판정합니다.
# 0.75는 강의용 출발점입니다. 문장 종류에 따라 조금씩 조정할 수 있습니다.
threshold = 0.75

# 문장 임베딩 모델 이름
# paraphrase-multilingual-... : 여러 언어(독일어 포함)의 패러프레이즈 비교에 맞춘 모델
# MiniLM-L12-v2               : 비교적 작고 빠른 버전 (벡터 길이 384)
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"


# =====================================================
# 함수들
# 같은 일을 여러 문장 쌍에 반복하므로, 미리 절차를 함수로 적어 둡니다.
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


def collect_unique_sentences(pairs):
    """문장 쌍 목록에서, 중복 없이 문장을 모읍니다.

    같은 문장이 여러 쌍에 나와도 벡터는 한 번만 만들면 됩니다.
    순서는 처음 나온 차례를 유지합니다.
    """
    sentences = []
    seen = set()  # 이미 넣은 문장을 기억합니다.
    for _name, s1, s2 in pairs:
        for sentence in (s1, s2):
            if sentence not in seen:
                seen.add(sentence)
                sentences.append(sentence)
    return sentences


def sentences_to_vectors(sentences, model):
    """각 문장을 임베딩 벡터(숫자 목록)로 바꿉니다.

    encode():
      문장 여러 개를 한 번에 넣으면, 문장마다 벡터 하나씩 나옵니다.
      모든 벡터의 길이는 같습니다 (이 모델은 보통 384).

    결과는 {문장: 벡터} 딕셔너리입니다.
    쌍 비교는 이 딕셔너리에서 문장을 찾아 점수를 계산합니다.
    """
    # convert_to_numpy=True → 각 벡터를 숫자 배열로 받습니다.
    embeddings = model.encode(sentences, convert_to_numpy=True)

    vectors = {}
    for sentence, embedding in zip(sentences, embeddings):
        # .tolist(): numpy 배열을 일반 숫자 목록으로 바꿉니다.
        # 17번의 cosine()과 같은 방식으로 계산하기 위해서입니다.
        vectors[sentence] = embedding.tolist()
    return vectors


def cosine(a, b):
    """두 벡터의 코사인 유사도를 계산합니다. 이것이 의미 유사도 점수입니다.

    공식:  cos(a, b) = (a·b) / (|a| × |b|)

      a·b  : 내적. 같은 위치의 숫자를 곱한 뒤 모두 더함
      |a|  : a의 길이(크기). 각 숫자를 제곱해 더한 뒤 제곱근
      결과 : 보통 -1 ~ 1. 문장 임베딩은 비슷한 의미일수록 1에 가깝습니다.

    13번(Bag-of-Words)·14번(TF-IDF)·17번(문장 임베딩)과 같은 공식입니다.
    """
    # zip: 두 목록에서 같은 위치의 값을 짝지어 꺼냅니다.
    dot = sum(x * y for x, y in zip(a, b))  # 내적
    na = sqrt(sum(x * x for x in a))        # a의 길이
    nb = sqrt(sum(y * y for y in b))        # b의 길이

    # 길이가 0이면 나눌 수 없습니다.
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def pair_scores(pairs, vectors):
    """문장 쌍마다 의미 유사도 점수를 계산합니다.

    결과는 [(이름, 문장1, 문장2, 점수), ...] 목록입니다.
    점수는 20번 원래 예처럼 문장 두 개와 함께 쓸 수 있습니다.
    """
    results = []
    for name, s1, s2 in pairs:
        score = cosine(vectors[s1], vectors[s2])
        results.append((name, s1, s2, score))
    return results


def judge_paraphrase(score, threshold):
    """점수와 임계값을 비교해 패러프레이즈 여부를 판정합니다.

    score >= threshold  → 패러프레이즈
    score <  threshold  → 비패러프레이즈

    임계값은 "이 정도면 의미가 비슷하다"고 정한 선입니다.
    정답이 아니라, 과제에 맞춰 정하는 기준입니다.
    """
    if score >= threshold:
        return "패러프레이즈"
    return "비패러프레이즈"


def interpret_judgment(score, threshold):
    """판정 이유를 초보자가 읽을 수 있게 한 줄로 적습니다.

    점수가 높은 쌍: 핵심 사건 의미가 비슷하다고 모델이 본 경우
    점수가 낮은 쌍: 주제나 사건이 다르다고 모델이 본 경우
    """
    if score >= threshold:
        return "핵심 사건 의미가 유사함"
    return "주제와 사건 의미가 다름"


# =====================================================
# 실행 부분: 위에서 만든 함수를 실제로 순서대로 호출합니다.
# =====================================================

print("1) 비교할 문장 쌍")
print(f"   임계값(threshold): {threshold:.2f}")
print("   이 점수 이상이면 패러프레이즈로 판정합니다.")
for name, s1, s2 in pairs:
    print(f"- {name}")
    print(f"  문장 1: {s1}")
    print(f"  문장 2: {s2}")
print("-" * 50)


# 2) 모델을 불러, 등장하는 문장을 한 번씩만 벡터로 바꿉니다.
model = load_embedder(MODEL_NAME)
unique_sentences = collect_unique_sentences(pairs)
vectors = sentences_to_vectors(unique_sentences, model)

print("2) 임베딩 벡터")
print("   각 문장이 같은 길이의 숫자 목록이 됩니다.")
for sentence in unique_sentences:
    vector = vectors[sentence]
    preview = [round(x, 3) for x in vector[:6]]  # 앞 6개만 보여 줍니다.
    print(f"- {sentence}")
    print(f"  벡터 길이: {len(vector)}")
    print(f"  앞부분: {preview} ...")
print("-" * 50)


print("3) 의미 유사도 점수와 패러프레이즈 판정")
print("   점수는 코사인 유사도입니다. 1에 가까울수록 의미가 비슷합니다.")
print(f"   판정 규칙: 점수 >= {threshold:.2f} 이면 패러프레이즈")
scores = pair_scores(pairs, vectors)
for name, s1, s2, score in scores:
    label = judge_paraphrase(score, threshold)
    reason = interpret_judgment(score, threshold)
    print(f"- {name}")
    print(f"  문장 1: {s1}")
    print(f"  문장 2: {s2}")
    print(f"  유사도: {score:.2f} → {label}")
    print(f"  해석: {reason}")
print("-" * 50)

# 이 예에서 대략 이렇게 나와야 합니다.
#   기차-도착 : 높음 → 패러프레이즈
#       kommt/erreicht, pünktlich/rechtzeitig 처럼 단어는 달라도
#       "기차가 제시간에 도착한다"는 사건 의미가 비슷합니다.
#   강의-시작 : 높음 → 패러프레이즈
#       beginnen ≈ starten, 어순만 바뀐 경우입니다.
#   책-비행   : 낮음 → 비패러프레이즈
#       책을 읽는 일과 내일 빈으로 가는 일은 주제가 다릅니다.

# 문장 쌍을 바꾸고 싶다면 pairs만 아래처럼 바꾸면 됩니다.
# pairs = [
#     ("예1", "Ich lese ein Buch.", "Ich schlage ein Buch auf."),
#     ("예2", "Ich lese ein Buch.", "Ich fliege nach Berlin."),
# ]

# 판정을 더 엄격하게 하려면 threshold를 올리면 됩니다.
# threshold = 0.85
