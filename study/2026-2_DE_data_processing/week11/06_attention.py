"""06. Attention: self-attention 가중치와 attention map 시각화

Self-Attention이란?
- 문장 안 각 토큰이 "다른 토큰을 얼마나 참고할지" 비중을 계산하는 방법입니다.
- Query(질문) · Key(검색키) · Value(값) 세 가지 역할을 둡니다.
- 이 실습에서는 교육용으로 Q = K = V = X 로 단순화해 원리를 봅니다.

Scaled Dot-Product Attention 점수:
  score(i, j) = (Q_i · K_j) / sqrt(d_k)

필요 패키지:
  pip install numpy matplotlib seaborn
"""

import platform

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


# ------------------------------------------------------------
# 기본 설정값 (수업/실습용)
# ------------------------------------------------------------
# 예문: Der Hund jagt die Katze. (개가 고양이를 쫓는다)
# 실제 모델은 서브워드 토큰을 쓰지만, 여기서는 단어 단위로 원리를 봅니다.
DEFAULT_TOKENS = ["Der", "Hund", "jagt", "die", "Katze"]

# 교육용 토큰 벡터: 실제 언어모델의 학습 벡터가 아닙니다.
#   각 행 = 한 토큰, 각 열 = 가상의 특징 차원 (여기서는 3차원)
#   비슷한 숫자 패턴 → 내적(관련도 점수)이 커집니다.
#   예) Hund 와 Katze 는 서로 비슷하게 잡아 두었습니다.
DEFAULT_VECTORS = np.array(
    [
        [0.2, 0.1, 0.6],  # Der
        [0.9, 0.1, 0.2],  # Hund
        [0.6, 0.6, 0.1],  # jagt
        [0.1, 0.2, 0.5],  # die
        [0.8, 0.2, 0.3],  # Katze
    ],
    dtype=float,
)


def setup_korean_font():
    """matplotlib에서 한글이 깨지지 않도록 OS별 기본 글꼴을 지정합니다."""
    # matplotlib 기본 글꼴(DejaVu Sans)은 한글 글리프가 없어 □로 깨집니다.
    if platform.system() == "Windows":
        plt.rcParams["font.family"] = "Malgun Gothic"  # 맑은 고딕
    elif platform.system() == "Darwin":
        plt.rcParams["font.family"] = "AppleGothic"  # macOS
    else:
        plt.rcParams["font.family"] = "NanumGothic"  # Linux (나눔고딕 설치 필요)
    plt.rcParams["axes.unicode_minus"] = False


def softmax_rows(scores):
    """행 단위 softmax를 계산합니다.

    - 각 행의 합이 1이 되도록 정규화합니다.
    - 행의 최댓값을 먼저 빼서 지수 폭주를 막습니다(수치 안정화).

    반환값
    - weights[i, j] = 토큰 i(Query)가 토큰 j(Key)를 참고하는 비중
    """
    shifted = scores - scores.max(axis=1, keepdims=True)
    exp_scores = np.exp(shifted)
    return exp_scores / exp_scores.sum(axis=1, keepdims=True)


def compute_attention_weights(vectors):
    """토큰 벡터 행렬로부터 self-attention 가중치를 계산합니다.

    이 예제에서는 Q = K = V = X (별도의 선형 변환 W_Q, W_K, W_V 없음).
    실제 Transformer에서는 Q, K, V를 각각 다른 가중치로 투영합니다.

    매개변수
    - vectors: shape (토큰수, 차원)

    반환값
    - scores  : 스케일된 내적 점수 행렬
    - weights : softmax 가중치 행렬
    """
    vectors = np.asarray(vectors, dtype=float)
    if vectors.ndim != 2:
        raise ValueError("vectors 는 2차원 배열이어야 합니다. (토큰수, 차원)")

    # X @ X.T : 모든 토큰 쌍의 내적 → (N, N) 점수 행렬
    # / sqrt(d_k) : softmax가 너무 뾰족해지지 않게 스케일링
    d_k = vectors.shape[1]
    scores = vectors @ vectors.T / np.sqrt(d_k)
    weights = softmax_rows(scores)
    return scores, weights


def plot_attention_map(weights, tokens, title=None, show=True):
    """attention 가중치를 히트맵으로 그립니다.

    - 행 = 현재 토큰(Query)
    - 열 = 참고되는 토큰(Key)

    실제 모델에서는 이 가중치로 Value를 가중합해 문맥 벡터를 만듭니다.
      context_i = Σ_j weights[i, j] * V[j]
    이 코드는 가중치 분포만 시각화하고, Value 가중합은 생략합니다.
    """
    if len(tokens) != weights.shape[0]:
        raise ValueError("tokens 개수와 weights 행 수가 일치해야 합니다.")

    if title is None:
        title = "Self-Attention Map: 행 토큰이 열 토큰을 참고하는 비중"

    # A/B 데모를 연속 실행할 때 그래프가 겹치지 않도록 새 figure를 만듭니다.
    plt.figure()
    sns.heatmap(
        weights,
        annot=True,
        fmt=".2f",
        cmap="YlOrRd",
        xticklabels=tokens,
        yticklabels=tokens,
    )
    plt.title(title)
    plt.xlabel("참고되는 토큰 (Key)")
    plt.ylabel("현재 토큰 (Query)")
    plt.tight_layout()
    if show:
        plt.show()


def print_attention_report(tokens, weights, digits=3):
    """가중치 합과 행렬을 초보자가 읽기 쉽게 출력합니다."""
    row_sums = weights.sum(axis=1)
    print("토큰:", tokens)
    print("각 행의 가중치 합:", np.round(row_sums, digits))
    print("(각 행의 합이 1에 가까우면 softmax가 올바르게 적용된 것입니다.)")
    print()
    print("Attention 가중치 행렬:")
    print(np.round(weights, digits))
    print()
    print("관찰 포인트:")
    print("  - 값이 클수록 해당 Key 토큰을 더 많이 참고합니다.")
    print("  - 비슷한 벡터끼리 내적이 커서 가중치가 커지는 경향이 있습니다.")
    print("  - 실제 모델은 학습된 W_Q, W_K, W_V 로 Q/K/V를 만듭니다.")


def run_attention_demo(tokens=None, vectors=None, show_plot=True):
    """토큰·벡터를 받아 attention을 계산하고 출력/시각화합니다.

    이 함수만 호출해도 전체 실습 흐름이 실행됩니다.
    """
    tokens = list(DEFAULT_TOKENS if tokens is None else tokens)
    vectors = DEFAULT_VECTORS if vectors is None else np.asarray(vectors, dtype=float)

    if len(tokens) != len(vectors):
        raise ValueError("tokens 개수와 vectors 행 수가 같아야 합니다.")

    setup_korean_font()
    _, weights = compute_attention_weights(vectors)
    print_attention_report(tokens, weights)
    plot_attention_map(weights, tokens, show=show_plot)
    return weights


def read_tokens_from_input():
    """사용자에게 토큰을 공백으로 구분해 입력받습니다.

    빈 입력이면 기본 예제 토큰을 사용합니다.
    """
    print("토큰을 공백으로 구분해 입력하세요.")
    print("(예: Der Hund jagt die Katze / 빈 입력이면 기본 예제 사용)")
    line = input("> ").strip()
    if not line:
        return list(DEFAULT_TOKENS)
    tokens = line.split()
    if len(tokens) < 2:
        raise ValueError("attention을 보려면 토큰이 2개 이상 필요합니다.")
    return tokens


def make_random_vectors(n_tokens, dim=3, seed=42):
    """데모용 난수 벡터를 만듭니다. (사용자 입력 토큰용)"""
    rng = np.random.default_rng(seed)
    return rng.random((n_tokens, dim))


if __name__ == "__main__":
    # --------------------------------------------------
    # A. 기본 데모: 미리 준비한 토큰·벡터로 attention 관찰
    # --------------------------------------------------
    print("=" * 60)
    print("A. 기본 데모 (Der Hund jagt die Katze)")
    print("=" * 60)
    run_attention_demo()
    print()

    # --------------------------------------------------
    # B. 일반화: 사용자가 입력한 토큰으로 같은 절차 반복
    #    (벡터는 교육용 난수로 생성)
    # --------------------------------------------------
    print("=" * 60)
    print("B. 직접 입력한 토큰으로 관찰하기")
    print("=" * 60)
    user_tokens = read_tokens_from_input()
    user_vectors = make_random_vectors(len(user_tokens))
    print()
    print("참고: 직접 입력한 토큰에는 교육용 난수 벡터를 사용합니다.")
    print("      (실제 의미 관계가 아니라 '계산 절차'를 보는 용도입니다.)")
    print()
    run_attention_demo(tokens=user_tokens, vectors=user_vectors)
