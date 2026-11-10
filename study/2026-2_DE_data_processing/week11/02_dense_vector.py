"""02. Dense vector: 저차원 실수 벡터로 단어를 표현

Dense vector(밀집 벡터)란?
- One-hot은 "어휘 크기"만큼 차원이 크고, 값이 거의 전부 0입니다. (희소 벡터)
- Dense vector는 훨씬 낮은 차원(예: 50, 300, 384)의 실수 값으로 단어를 표현합니다.
- 비슷한 의미의 단어는 비슷한 벡터를 갖는 경향이 있습니다.

예) 사전학습 모델로 구한 벡터 (앞부분만 표시)
  Hund  ≈ [0.02, -0.11, ...]
  Katze ≈ [0.01, -0.09, ...]  ← Hund와 방향이 비슷한 경향
  Auto  ≈ [-0.05, 0.20, ...]  ← 동물 단어와는 다른 경향

주의:
- 실제 임베딩에서는 각 차원이 사람이 바로 해석하기 어려운 경우가 많습니다.
- 아래 A절은 사전학습 모델로 "진짜" dense vector를 구합니다.
- B절은 학습 전 상태를 보여 주기 위한 랜덤 벡터 예제입니다.

필요 패키지:
  pip install sentence-transformers
"""

import numpy as np

# pip install sentence-transformers
from sentence_transformers import SentenceTransformer


def build_vocab(tokens):
    """토큰 목록에서 중복을 제거해 어휘(vocabulary)를 만듭니다.

    - 등장 순서를 유지합니다.
    - 같은 단어가 여러 번 나와도 어휘에는 한 번만 들어갑니다.
    """
    vocab = []
    seen = set()
    for token in tokens:
        if token not in seen:
            vocab.append(token)
            seen.add(token)
    return vocab


def make_random_dense_vectors(vocab, dim=8, seed=42):
    """어휘의 각 단어에 랜덤한 dense vector를 부여합니다.

    실제 신경망도 처음에는 이런 식으로 벡터를 무작위로 시작한 뒤,
    학습을 통해 "의미가 비슷한 단어끼리 비슷한 벡터"가 되도록 조정합니다.

    매개변수
    - vocab: 단어 목록
    - dim  : 벡터 차원 수 (one-hot보다 훨씬 작게 둡니다)
    - seed : 난수 시드 (같은 값이면 매번 같은 결과가 나옵니다)
    """
    rng = np.random.default_rng(seed)
    # shape = (어휘 크기, 차원 수)
    # 값을 -1 ~ 1 사이의 실수로 만듭니다.
    matrix = rng.uniform(low=-1.0, high=1.0, size=(len(vocab), dim))
    return {word: matrix[i] for i, word in enumerate(vocab)}


def make_toy_dense_vectors(
    words=("Hund", "Katze", "Auto"),
    model_name="paraphrase-multilingual-MiniLM-L12-v2",
):
    """사전학습 모델로 단어(또는 짧은 텍스트)의 실제 dense vector를 구합니다.

    사용 모델
    - paraphrase-multilingual-MiniLM-L12-v2
      : 여러 언어를 같은 벡터 공간에 올리는 문장 임베딩 모델
      : 단어 하나도 "짧은 문장"처럼 넣어 벡터로 바꿀 수 있습니다.
      : 처음 실행 시 모델 가중치를 인터넷에서 다운로드합니다.

    반환값
    - {단어: numpy 벡터} 형태의 사전
    - 각 벡터 차원은 보통 384입니다.
    """
    # 1) 사전학습된 임베딩 모델 불러오기
    model = SentenceTransformer(model_name)

    # 2) encode: 각 단어를 고정 길이 실수 벡터로 변환
    #    convert_to_numpy=True → NumPy 배열로 바로 받음
    embeddings = model.encode(list(words), convert_to_numpy=True)

    # 3) 단어 → 벡터 사전으로 정리
    return {word: embeddings[i] for i, word in enumerate(words)}


def cosine_similarity(a, b):
    """두 벡터의 코사인 유사도를 계산합니다. (-1 ~ 1)

    1에 가까울수록 방향이 비슷 = 의미가 비슷하다고 해석할 수 있습니다.
    (다음 실습 03에서 더 자세히 다룹니다.)
    """
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def get_vector(word, vectors):
    """단어에 해당하는 dense vector를 조회합니다."""
    if word not in vectors:
        raise KeyError(f"벡터 사전에 없는 단어입니다: '{word}'")
    return vectors[word]


def describe_vector(word, vector):
    """벡터의 기본 정보를 초보자용으로 요약합니다."""
    nonzero = np.count_nonzero(vector)
    return {
        "word": word,
        "vector": vector,
        "dim": vector.size,          # 차원 수
        "dtype": vector.dtype,       # 자료형 (보통 float)
        "nonzero": nonzero,          # 0이 아닌 값의 개수
        "density": nonzero / vector.size,  # 밀집도 (1에 가까울수록 밀집)
    }


def average_vectors(tokens, vectors):
    """문장의 단어 벡터를 평균내어 문장 벡터를 만듭니다.

    - 가장 단순한 문장 표현 방법 중 하나입니다.
    - 나중에 배우는 sentence embedding의 기초 아이디어입니다.
    """
    chosen = [get_vector(token, vectors) for token in tokens]
    return np.mean(chosen, axis=0)


def print_vector_table(vectors, preview=8):
    """단어별 dense vector를 표처럼 출력합니다.

    - 차원이 클 수 있으므로 앞부분 preview개만 보여 줍니다.
    """
    print("[단어별 dense vector]")
    for word, vector in vectors.items():
        info = describe_vector(word, vector)
        # 앞부분만 보여 주고, 전체가 더 길면 ... 표시
        pretty = np.round(vector[:preview], 3)
        suffix = " ..." if vector.size > preview else ""
        print(
            f"  {word:>10} -> {pretty}{suffix}  "
            f"(차원={info['dim']}, 밀집도={info['density']:.2f})"
        )


if __name__ == "__main__":
    # --------------------------------------------------
    # A. 실제 예제: 사전학습 모델로 Hund / Katze / Auto 벡터 구하기
    # --------------------------------------------------
    print("=" * 60)
    print("A. 사전학습 모델 dense vector (Hund / Katze / Auto)")
    print("=" * 60)

    real_vectors = make_toy_dense_vectors()
    print_vector_table(real_vectors)
    print()

    # 의미가 비슷한 단어끼리 벡터도 비슷한지 간단히 확인
    hund = real_vectors["Hund"]
    katze = real_vectors["Katze"]
    auto = real_vectors["Auto"]
    print("[코사인 유사도 미리보기]")
    print(f"  Hund–Katze: {cosine_similarity(hund, katze):.3f}")
    print(f"  Hund–Auto : {cosine_similarity(hund, auto):.3f}")
    print(f"  Katze–Auto: {cosine_similarity(katze, auto):.3f}")
    print()
    print("관찰 포인트:")
    print("  - 손으로 숫자를 넣지 않고, 모델이 계산한 실제 벡터입니다.")
    print("  - 보통 Hund–Katze 유사도가 Hund–Auto보다 높게 나옵니다.")
    print("  - 차원이 수백 개여도 one-hot처럼 어휘 크기만큼 커지지는 않습니다.")
    print("  - 각 차원의 의미를 사람이 하나씩 해석하기는 어렵습니다.")
    print()

    # --------------------------------------------------
    # B. 일반화 예제: 입력 문장 → 어휘 → 랜덤 dense vector
    # --------------------------------------------------
    print("=" * 60)
    print("B. 일반화: 입력 문장으로 dense vector 만들기")
    print("=" * 60)

    text = input("문장을 입력하세요: ").strip()
    if not text:
        raise ValueError("빈 문장입니다. 단어를 하나 이상 입력하세요.")

    # 1) 공백 기준 토큰화 + 소문자 통일
    tokens = text.lower().split()

    # 2) 어휘 구축
    vocab = build_vocab(tokens)

    # 3) 원하는 차원 수 입력 (기본값 8)
    dim_text = input("벡터 차원 수를 입력하세요 (기본 8): ").strip()
    dim = int(dim_text) if dim_text else 8
    if dim <= 0:
        raise ValueError("차원 수는 1 이상의 정수여야 합니다.")

    # 4) 어휘의 각 단어에 dense vector 부여
    vectors = make_random_dense_vectors(vocab, dim=dim, seed=42)

    print()
    print("원문 토큰:", tokens)
    print("어휘(vocab):", vocab)
    print("어휘 크기:", len(vocab))
    print("벡터 차원:", dim)
    print()

    # 5) 단어별 벡터 확인
    print_vector_table(vectors)
    print()

    # 6) one-hot과 비교해서 차이 강조
    print("[one-hot vs dense 한눈에 비교]")
    print(f"  one-hot 차원 예: 어휘 크기와 같음 → {len(vocab)}")
    print(f"  dense  차원 예: 사용자가 정한 값   → {dim}")
    print("  one-hot: 해당 위치만 1, 나머지 0 (희소)")
    print("  dense : 거의 모든 차원이 0이 아닌 실수 (밀집)")
    print()

    # 7) 문장 전체를 평균 벡터로 요약
    sentence_vector = average_vectors(tokens, vectors)
    print("[문장 평균 벡터] (bag-of-embeddings의 아주 단순한 형태)")
    print(np.round(sentence_vector, 3))
    print("차원=", sentence_vector.size)
