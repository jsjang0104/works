"""10. 문장 의미 분석 시각화

문장 임베딩(의미 벡터)을 만들고,
PCA로 2차원에 투영한 뒤
문장 간 의미 차이(1 - 코사인 유사도)를 그래프로 보여 줍니다.
비슷한 문장은 가깝게, 다른 문장은 멀게 나타납니다.
"""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

# 문장 목록만 바꾸면 좌표(coords)와 그림이 자동으로 다시 만들어진다.
sentences = [
    "Ich lese ein Buch.",          # 독서
    "Ich studiere Linguistik.",    # 학습 (비교적 유사할 수 있음)
    "Das Wetter ist schön.",       # 날씨 (주제 다름)
]


def encode_sentences(sentences, model_name="paraphrase-multilingual-MiniLM-L12-v2"):
    """다국어 문장 임베딩 모델로 각 문장의 의미벡터를 만든다."""
    model = SentenceTransformer(model_name)
    return np.asarray(model.encode(sentences))


def reduce_to_2d(vectors):
    """고차원 의미벡터를 2차원 좌표로 축소한다 (시각화용)."""
    n_samples, n_features = vectors.shape
    # 문장 수가 2개 미만이면 축을 1개만 쓸 수 있음
    n_components = min(2, n_samples, n_features)
    coords_2d = PCA(n_components=n_components, random_state=42).fit_transform(vectors)
    # 1차원만 나온 경우 y=0으로 채워 2차원처럼 맞춤
    if coords_2d.shape[1] == 1:
        coords_2d = np.column_stack([coords_2d[:, 0], np.zeros(n_samples)])
    return coords_2d


def make_coords(sentences, coords_2d):
    """문장별 2차원 좌표 사전을 자동으로 만든다."""
    return {
        sentence: (float(x), float(y))
        for sentence, (x, y) in zip(sentences, coords_2d)
    }


def meaning_differences(vectors):
    """문장 쌍의 의미 차이(1 - 코사인 유사도)를 계산한다.
    차이가 0에 가까우면 의미가 비슷하고, 1에 가까우면 다르다.
    """
    similarity = cosine_similarity(vectors)
    return 1.0 - similarity


def plot_sentence_semantics(sentences, coords, differences):
    """문장 의미 공간과 문장 사이 의미 차이를 시각화한다."""
    xs = np.array([coords[s][0] for s in sentences])
    ys = np.array([coords[s][1] for s in sentences])
    # 점과 라벨이 겹치지 않도록 여백 계산
    x_pad = (xs.max() - xs.min()) * 0.15 or 0.1
    y_pad = (ys.max() - ys.min()) * 0.15 or 0.1
    colors = plt.cm.tab10(np.linspace(0, 0.9, len(sentences)))

    fig, ax = plt.subplots(figsize=(8, 6))

    # 문장 쌍을 선으로 잇고, 중간에 의미 차이 값을 표시
    for i in range(len(sentences)):
        for j in range(i + 1, len(sentences)):
            ax.plot(
                [xs[i], xs[j]],
                [ys[i], ys[j]],
                color="#cfcfcf",
                linewidth=1.2,
                zorder=1,
            )
            ax.text(
                (xs[i] + xs[j]) / 2,
                (ys[i] + ys[j]) / 2,
                f"차이 {differences[i, j]:.2f}",
                fontsize=8,
                color="#555555",
                ha="center",
                va="center",
                zorder=2,
            )

    # 각 문장을 점으로 표시
    for i, sentence in enumerate(sentences):
        ax.scatter(xs[i], ys[i], s=160, color=colors[i], zorder=3, label=sentence)
        ax.text(xs[i] + x_pad * 0.12, ys[i] + y_pad * 0.08, sentence, fontsize=9, zorder=4)

    ax.set_xlim(xs.min() - x_pad, xs.max() + x_pad)
    ax.set_ylim(ys.min() - y_pad, ys.max() + y_pad)
    ax.set_xlabel("의미 공간 축 1 (PCA)")
    ax.set_ylabel("의미 공간 축 2 (PCA)")
    ax.set_title("문장 의미 공간과 의미 차이")
    ax.legend(loc="best", fontsize=8, frameon=True)
    fig.tight_layout()
    plt.show()


if __name__ == "__main__":
    # 1) 임베딩 → 2) 2차원 축소 → 3) 차이 계산 → 4) 시각화
    vectors = encode_sentences(sentences)
    coords_2d = reduce_to_2d(vectors)
    coords = make_coords(sentences, coords_2d)
    differences = meaning_differences(vectors)

    print("자동 생성된 문장 좌표(coords)")
    for sentence, (x, y) in coords.items():
        print(f"- {sentence}: ({x:.3f}, {y:.3f})")

    print("\n문장 쌍 의미 차이")
    for i in range(len(sentences)):
        for j in range(i + 1, len(sentences)):
            print(f"- {sentences[i]}  ↔  {sentences[j]}: {differences[i, j]:.3f}")

    plot_sentence_semantics(sentences, coords, differences)
