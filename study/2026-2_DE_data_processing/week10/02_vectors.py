"""문장에서 벡터를 만들고, 덧셈·내적·코사인 유사도를 계산합니다.

자연어처리에서 단어·문장은 글자입니다.
컴퓨터가 다루려면 각 문장을 "숫자들의 목록(벡터)"으로 바꿔야 합니다.

이 실습은 숫자를 손으로 넣지 않습니다.
문장을 단어로 쪼갠 뒤, 단어가 몇 번 나왔는지를 세어 행렬을 만듭니다.
같은 코드에 다른 문장을 넣어도 벡터가 자동으로 다시 계산됩니다.

그다음
- 비슷한 문장은 가까운 방향
- 다른 문장은 먼 방향
을 코사인 유사도와 3차원 그림으로 확인합니다.
"""

# numpy: 벡터·행렬 계산
# pandas: 단어 빈도 표를 보기 쉽게 출력
# CountVectorizer: 문장 목록 → 문서-단어 행렬
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer

# Windows에서 그래프 한글이 깨지지 않도록 글꼴을 지정합니다.
plt.rc("font", family="Malgun Gothic")
plt.rc("axes", unicode_minus=False)


# ---------------------------------------------------------------------------
# 1) 비교할 문장
#    이 딕셔너리만 바꿔도 아래 벡터·유사도·그림이 모두 다시 계산됩니다.
# ---------------------------------------------------------------------------
texts = {
    "haus": "Ich wohne in einem großen Haus. Das Haus ist schön.",
    "wohnung": "Ich wohne in einer kleinen Wohnung. Die Wohnung ist schön.",
    "garten": "Der Garten vor dem Haus ist schön.",
    "auto": "Das Auto fährt schnell auf der Straße.",
    "zug": "Der Zug fährt schnell auf der Straße.",
}

labels = list(texts.keys())       # 각 문장을 가리키는 짧은 이름
sentences = list(texts.values())  # 실제 문장


def sentences_to_matrix(sentences):
    """문장 리스트를 문서-단어 행렬(숫자 표)로 바꿉니다.

    각 행 = 한 문장, 각 열 = 한 단어, 칸 안의 숫자 = 그 단어가 나온 횟수.
    숫자를 임의로 정하지 않고, 문장에서 직접 세어 얻습니다.
    """
    vectorizer = CountVectorizer()
    # fit_transform: 단어 목록을 만들고, 동시에 횟수를 셉니다.
    # toarray(): 희소 행렬을 일반 숫자 표(numpy 배열)로 바꿉니다.
    matrix = vectorizer.fit_transform(sentences).toarray().astype(float)
    words = vectorizer.get_feature_names_out()
    return matrix, words


def cosine_similarity(a, b):
    """두 벡터가 가리키는 방향이 얼마나 비슷한지 계산합니다.

    공식: (a · b) / (|a| × |b|)
    - 분자: 내적 (겹치는 정도)
    - 분모: 각 벡터의 길이(norm). 길이 차이를 없애고 "방향"만 비교합니다.
    - 1에 가까우면 같은 방향(겹치는 단어·의미가 많음)
    - 0에 가까우면 서로 직각(겹치는 것이 거의 없음)
    """
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def cosine_matrix(matrix):
    """여러 벡터를 한 번에 비교해 코사인 유사도 표를 만듭니다."""
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    # 길이가 0인 벡터(빈 문장)는 나누기 오류를 막기 위해 1로 둡니다.
    safe_norms = np.where(norms == 0, 1.0, norms)
    unit = matrix / safe_norms
    return unit @ unit.T


def reduce_to_3d(matrix):
    """고차원 문장 벡터를 3차원 좌표로 줄입니다.

    SVD는 평균을 빼지 않으므로, 원점에서 본 방향(코사인 유사도)을
    가능한 한 그대로 남깁니다. 단어가 3개보다 적어도 빈 축을 채워
    항상 (문장 수 × 3) 좌표를 돌려줍니다.
    """
    # 문장 벡터가 모두 0이면 그림에 쓸 좌표도 0으로 둡니다.
    if np.allclose(matrix, 0):
        return np.zeros((matrix.shape[0], 3))

    # SVD: matrix ≈ U × S × V^T
    # U × S 의 앞 3열이 3차원에서 문장의 위치에 해당합니다.
    U, S, _ = np.linalg.svd(matrix, full_matrices=False)
    k = min(3, len(S))
    coords = U[:, :k] * S[:k]
    if k < 3:
        coords = np.pad(coords, ((0, 0), (0, 3 - k)))
    return coords


def l2_normalize_rows(matrix):
    """각 행 벡터의 길이를 1로 맞춥니다. 코사인은 방향만 보므로 길이를 통일합니다."""
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    safe_norms = np.where(norms == 0, 1.0, norms)
    return matrix / safe_norms


def draw_angle_arc(ax, vec_a, vec_b, radius=0.35, color="gray"):
    """두 단위 벡터 사이의 각을 작은 호로 그립니다."""
    a = vec_a / np.linalg.norm(vec_a)
    b = vec_b / np.linalg.norm(vec_b)
    cos = float(np.clip(np.dot(a, b), -1.0, 1.0))
    theta = np.arccos(cos)
    if theta < 1e-6:
        return

    # a와 직각인 방향으로 b를 분해해, a에서 b로 돌아가는 평면을 만듭니다.
    b_orth = b - np.dot(b, a) * a
    orth_norm = np.linalg.norm(b_orth)
    if orth_norm < 1e-12:
        return
    b_orth = b_orth / orth_norm
    ts = np.linspace(0.0, theta, 40)
    pts = radius * (np.outer(np.cos(ts), a) + np.outer(np.sin(ts), b_orth))
    ax.plot(pts[:, 0], pts[:, 1], pts[:, 2], color=color, lw=2)


def plot_cosine_3d(matrix, labels, sim):
    """문장 벡터를 단위원 위의 화살표로 그리고, 코사인 유사도 표도 함께 보여 줍니다."""
    # 방향만 남긴 뒤 3차원으로 투영하고, 다시 길이를 1로 맞춥니다.
    coords = l2_normalize_rows(reduce_to_3d(l2_normalize_rows(matrix)))

    fig = plt.figure(figsize=(13, 6))
    ax3d = fig.add_subplot(1, 2, 1, projection="3d")
    ax_heat = fig.add_subplot(1, 2, 2)

    # (1) 단위원: 코사인 유사도는 "각도"이므로 모든 화살표를 같은 길이로 그립니다.
    u = np.linspace(0, 2 * np.pi, 36)
    v = np.linspace(0, np.pi, 18)
    sphere_x = np.outer(np.cos(u), np.sin(v))
    sphere_y = np.outer(np.sin(u), np.sin(v))
    sphere_z = np.outer(np.ones_like(u), np.cos(v))
    ax3d.plot_wireframe(
        sphere_x, sphere_y, sphere_z,
        color="lightgray", linewidth=0.4, alpha=0.35,
    )

    colors = plt.cm.tab10(np.linspace(0, 1, len(labels), endpoint=False))
    for i, label in enumerate(labels):
        x, y, z = coords[i]
        ax3d.quiver(
            0, 0, 0, x, y, z,
            color=colors[i], arrow_length_ratio=0.12, lw=2.5,
        )
        ax3d.text(x * 1.18, y * 1.18, z * 1.18, label, color=colors[i], fontsize=11)

    # 가장 비슷한 쌍 / 가장 다른 쌍의 각을 호로 표시합니다.
    pair_sim = sim.copy()
    np.fill_diagonal(pair_sim, np.nan)
    i_hi, j_hi = np.unravel_index(np.nanargmax(pair_sim), pair_sim.shape)
    i_lo, j_lo = np.unravel_index(np.nanargmin(pair_sim), pair_sim.shape)
    draw_angle_arc(ax3d, coords[i_hi], coords[j_hi], radius=0.40, color="forestgreen")
    draw_angle_arc(ax3d, coords[i_lo], coords[j_lo], radius=0.28, color="crimson")

    ax3d.set_title(
        "3D 코사인 유사도\n"
        f"가까움: {labels[i_hi]}–{labels[j_hi]} ({pair_sim[i_hi, j_hi]:.2f})  "
        f"멂: {labels[i_lo]}–{labels[j_lo]} ({pair_sim[i_lo, j_lo]:.2f})"
    )
    ax3d.set_xlabel("SVD-1")
    ax3d.set_ylabel("SVD-2")
    ax3d.set_zlabel("SVD-3")
    ax3d.set_xlim(-1.2, 1.2)
    ax3d.set_ylim(-1.2, 1.2)
    ax3d.set_zlim(-1.2, 1.2)
    ax3d.set_box_aspect((1, 1, 1))  # 세 축 비율을 같게 해야 각도가 왜곡되지 않습니다.

    # (2) 코사인 유사도 표: 숫자가 클수록(밝은색) 두 문장의 방향이 비슷합니다.
    im = ax_heat.imshow(sim, vmin=0, vmax=1, cmap="YlOrRd")
    n = len(labels)
    ax_heat.set_xticks(range(n), labels)
    ax_heat.set_yticks(range(n), labels)
    for i in range(n):
        for j in range(n):
            ax_heat.text(j, i, f"{sim[i, j]:.2f}", ha="center", va="center")
    ax_heat.set_title("문장 사이 코사인 유사도")
    fig.colorbar(im, ax=ax_heat, fraction=0.046, pad=0.04)

    plt.tight_layout()
    plt.show()


# ---------------------------------------------------------------------------
# 2) 문장 → 벡터(행렬)
# ---------------------------------------------------------------------------
matrix, words = sentences_to_matrix(sentences)
table = pd.DataFrame(matrix, index=labels, columns=words)

print("문서-단어 행렬 (행=문장, 열=단어, 값=출현 횟수)")
print(table.to_string())
print()

# 각 문장 벡터를 이름에 담아 두면, 아래 덧셈·내적 예시가 읽기 쉽습니다.
vectors = {label: matrix[i] for i, label in enumerate(labels)}
haus = vectors["haus"]
wohnung = vectors["wohnung"]
auto = vectors["auto"]

# 벡터 덧셈: 같은 단어의 횟수를 각각 더합니다.
# 의미적으로는 "두 문장에 나온 단어를 합친 새 문장 벡터"입니다.
print("haus + wohnung =")
print(pd.Series(haus + wohnung, index=words).to_string())
print()

# 내적(dot product): 두 문장이 같은 단어를 얼마나 함께 가지고 있는지의 한 측정값
print("haus · wohnung =", np.dot(haus, wohnung))
print("haus · auto    =", np.dot(haus, auto))
print()

# ---------------------------------------------------------------------------
# 3) 코사인 유사도
# ---------------------------------------------------------------------------
sim = cosine_matrix(matrix)

print("cos(haus, wohnung) =", round(cosine_similarity(haus, wohnung), 3), "  # 주거 관련 단어가 겹침")
print("cos(haus, auto)    =", round(cosine_similarity(haus, auto), 3), "  # 겹치는 단어가 거의 없음")
print("cos(auto, zug)     =", round(cosine_similarity(vectors["auto"], vectors["zug"]), 3), "  # fährt/schnell/Straße가 겹침")
print()
print("코사인 유사도 표")
print(pd.DataFrame(np.round(sim, 3), index=labels, columns=labels).to_string())

# ---------------------------------------------------------------------------
# 4) 3차원 그림
#    왼쪽: 단위원 위 화살표 (방향이 가까울수록 코사인이 큼)
#    오른쪽: 모든 문장 쌍의 코사인 값
# ---------------------------------------------------------------------------
plot_cosine_3d(matrix, labels, sim)
