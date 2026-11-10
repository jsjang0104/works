"""01. One-hot encoding: 범주형 단어를 0/1 벡터로 변환

One-hot encoding이란?
- 단어 하나를 "길이 = 어휘 크기"인 벡터로 바꿉니다.
- 해당 단어의 위치만 1이고, 나머지는 모두 0입니다.
  예) 어휘 ['ich', 'lerne', 'deutsch'] 에서 'lerne'
      -> [0, 1, 0]
"""

import numpy as np


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


def make_word_to_id(vocab):
    """어휘의 각 단어에 고유한 정수 ID를 부여합니다.

    예) ['ich', 'lerne', 'deutsch']
        -> {'ich': 0, 'lerne': 1, 'deutsch': 2}
    """
    return {word: i for i, word in enumerate(vocab)}


def one_hot_encode(word, word_to_id):
    """단어 하나를 one-hot 벡터로 변환합니다.

    1) 먼저 어휘 크기만큼 0으로 채운 벡터를 만듭니다.
    2) 그 단어의 ID 위치만 1로 바꿉니다.
    """
    if word not in word_to_id:
        raise KeyError(f"어휘에 없는 단어입니다: '{word}'")

    vector = np.zeros(len(word_to_id), dtype=int)
    index = word_to_id[word]
    vector[index] = 1
    return vector


def one_hot_encode_sequence(tokens, word_to_id):
    """문장(토큰 목록) 전체를 one-hot 행렬로 변환합니다.

    결과 shape = (문장 길이, 어휘 크기)
    - 각 행(row) = 한 단어의 one-hot 벡터
    """
    return np.array([one_hot_encode(token, word_to_id) for token in tokens])


if __name__ == "__main__":
    # 1) 원하는 문장을 직접 입력받습니다. (공백 기준 토큰화)
    text = input("문장을 입력하세요: ").strip()
    if not text:
        raise ValueError("빈 문장입니다. 단어를 하나 이상 입력하세요.")
    tokens = text.lower().split()

    # 2) 어휘 구축 + 단어→ID 매핑
    vocab = build_vocab(tokens)
    word_to_id = make_word_to_id(vocab)

    print("원문 토큰:", tokens)
    print("어휘(vocab):", vocab)
    print("단어→ID:", word_to_id)
    print("어휘 크기(벡터 차원):", len(vocab))
    print()

    # 3) 단어별 one-hot 벡터 확인
    print("[단어별 one-hot 벡터]")
    for word in vocab:
        print(f"  {word:>8} (id={word_to_id[word]}) -> {one_hot_encode(word, word_to_id)}")
    print()

    # 4) 문장 전체를 행렬로 변환
    #    같은 단어가 반복되면 같은 one-hot 벡터가 다시 나타납니다.
    matrix = one_hot_encode_sequence(tokens, word_to_id)
    print("[문장 one-hot 행렬] shape =", matrix.shape)
    print(matrix)
