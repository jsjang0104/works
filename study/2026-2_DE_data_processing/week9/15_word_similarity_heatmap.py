"""15. 유사도 점수 Heatmap (일반화)

핵심 아이디어:
  13번(Bag-of-Words)과 14번(TF-IDF)은 항목 쌍의 유사도를
  아래와 같은 목록으로 남깁니다.

      scores = [(이름1, 이름2, 점수), (이름1, 이름3, 점수), ...]

  Heatmap은 "누가 누구와 얼마나 비슷한가"를 색으로 보여 줍니다.
  그러려면 쌍 목록을 정사각 행렬로 바꿔야 합니다.

      행렬[i, j] = i번째 항목과 j번째 항목의 유사도
      대각선(자기 자신)은 항상 1.0
      (A, B)와 (B, A)는 같은 점수입니다 (대칭).

이 프로그램이 하는 일 (3단계):
  1) scores에서 항목 이름을 모은다
  2) 이름 × 이름 정사각 행렬을 만든다
  3) 행렬을 heatmap으로 그린다

13번 scores든 14번 scores든, 같은 함수에 넣으면 됩니다.
항목 수·이름·점수 계산 방법이 바뀌어도 입력 형식만 지키면 됩니다.
"""

import os
import pandas as pd
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import font_manager

# =====================================================
# 한글 폰트 설정
# 그래프 제목·축 라벨의 한글이 깨지지 않게 합니다.
# set_theme()가 폰트를 덮어쓰므로, 테마를 먼저 두고 폰트를 나중에 맞춥니다.
# =====================================================
sns.set_theme(style="white")

font_path = r"C:\Windows\Fonts\malgun.ttf"
if os.path.exists(font_path):
    font_manager.fontManager.addfont(font_path)
    font_name = font_manager.FontProperties(fname=font_path).get_name()
    mpl.rcParams["font.family"] = font_name
    mpl.rcParams["font.sans-serif"] = [font_name]
    mpl.rcParams["axes.unicode_minus"] = False


# =====================================================
# 입력 설정
# 직접 손대는 곳은 여기입니다.
# 13번·14번이 만든 scores를 그대로 넣으면 heatmap이 그려집니다.
# 여러 개를 넣으면 나란히 비교합니다.
# =====================================================

# 각 값은 13번, 14번의 pairwise_scores()와 같은 형식입니다.
#   [(이름1, 이름2, 점수), ...]
# 자기 자신과의 쌍은 넣지 않아도 됩니다. 행렬을 만들 때 1.0으로 채웁니다.
score_sets = {
    "Bag-of-Words": [
        ("Haus", "Gebäude", 0.621),
        ("Haus", "Baum", 0.000),
        ("Gebäude", "Baum", 0.000),
    ],
    "TF-IDF": [
        ("Haus", "Gebäude", 0.379),
        ("Haus", "Baum", 0.000),
        ("Gebäude", "Baum", 0.000),
    ],
}


# =====================================================
# 함수들
# 쌍 목록 → 정사각 행렬 → heatmap
# 이 세 단계만 기억하면 됩니다.
# =====================================================

def collect_names(scores):
    """scores에 나온 이름을 처음 나타난 순서대로 모읍니다.

    예)
      [("Haus", "Gebäude", 0.6), ("Haus", "Baum", 0.0)]
      → ["Haus", "Gebäude", "Baum"]

    순서를 고정해야 행과 열의 칸이 같은 항목을 가리킵니다.
    """
    names = []
    for name1, name2, _score in scores:
        for name in (name1, name2):
            if name not in names:
                names.append(name)
    return names


def scores_to_matrix(scores, names=None, self_score=1.0):
    """쌍 목록을 정사각 유사도 행렬(DataFrame)로 바꿉니다.

    받는 형식:
      1) [(이름1, 이름2, 점수), ...]   ← 13번, 14번
      2) 이미 정사각인 DataFrame       ← 그대로 돌려줌

    만드는 방법:
      - 대각선(같은 이름끼리)은 self_score (기본 1.0)
      - (A, B) 점수는 (B, A)에도 같은 값으로 넣음 (대칭)
      - 목록에 없는 쌍은 0.0

    예)
      scores = [("Haus", "Gebäude", 0.621)]
      →
                Haus  Gebäude
        Haus     1.000   0.621
        Gebäude  0.621   1.000
    """
    if isinstance(scores, pd.DataFrame):
        return scores

    if names is None:
        names = collect_names(scores)

    # 먼저 모든 칸을 0.0으로 만들어 둡니다.
    matrix = pd.DataFrame(0.0, index=names, columns=names)

    # 자기 자신과의 유사도는 1.0입니다 (같은 벡터).
    for name in names:
        matrix.loc[name, name] = self_score

    # 쌍 점수를 위·아래 삼각형에 같이 넣습니다.
    for name1, name2, score in scores:
        matrix.loc[name1, name2] = score
        matrix.loc[name2, name1] = score

    return matrix


def draw_heatmap(matrix, title="유사도 Heatmap", ax=None, cmap="YlGnBu"):
    """한 장의 유사도 행렬을 heatmap으로 그립니다.

    annot=True : 칸 안에 숫자도 같이 보여 줍니다.
    vmin~vmax  : 색 눈금을 0~1로 고정합니다.
                 (코사인 유사도 범위와 맞추면 그림끼리 비교하기 쉽습니다.)
    """
    created_fig = ax is None
    if created_fig:
        n = len(matrix)
        plt.figure(figsize=(max(5.0, n * 1.4), max(4.0, n * 1.2)))
        ax = plt.gca()

    sns.heatmap(
        matrix,
        annot=True,      # 칸 안에 점수 표시
        fmt=".3f",       # 13번·14번 print와 같은 소수점 세 자리
        cmap=cmap,
        vmin=0,
        vmax=1,
        square=True,     # 칸을 정사각형으로
        ax=ax,
    )
    ax.set_title(title)

    if created_fig:
        plt.tight_layout()
        plt.show()


def draw_score_sets(score_sets, cmap="YlGnBu"):
    """여러 scores를 받아 heatmap을 그립니다.

    1개면 한 장, 2개 이상이면 나란히 그립니다.
    13번과 14번을 같이 넣으면 두 방법의 점수 차이를 바로 볼 수 있습니다.
    """
    items = list(score_sets.items())
    n = len(items)
    if n == 0:
        raise ValueError("score_sets가 비어 있습니다.")

    # 항목이 많아져도 칸이 너무 작아지지 않게, 그림 크기를 이름 수에 맞춥니다.
    sample_names = collect_names(items[0][1]) if not isinstance(items[0][1], pd.DataFrame) else list(items[0][1].index)
    cell = max(5.0, len(sample_names) * 1.4)

    fig, axes = plt.subplots(1, n, figsize=(cell * n, cell))
    if n == 1:
        axes = [axes]

    for ax, (title, scores) in zip(axes, items):
        matrix = scores_to_matrix(scores)
        draw_heatmap(matrix, title=title, ax=ax, cmap=cmap)

    fig.suptitle("단어 의미 유사도 Heatmap", y=1.02)
    plt.tight_layout()
    plt.show()


# =====================================================
# 실행 부분: 위에서 만든 함수를 실제로 순서대로 호출합니다.
# =====================================================

print("1) 쌍 목록 → 정사각 행렬")
print("   대각선은 1.000, (A,B)와 (B,A)는 같은 값입니다.")
for title, scores in score_sets.items():
    matrix = scores_to_matrix(scores)
    print(f"\n- {title}")
    print(matrix.round(3).to_string())
print("-" * 50)

print("2) Heatmap")
print("   색이 진할수록 두 항목이 더 비슷합니다.")
print("   이 예에서는 Haus–Gebäude만 점수가 있고, Baum과는 겹치는 내용어가 없습니다.")
draw_score_sets(score_sets)
print("-" * 50)

# 하나만 그리고 싶다면 아래처럼 쓰면 됩니다.
# draw_heatmap(scores_to_matrix(score_sets["Bag-of-Words"]), title="Bag-of-Words")
# draw_heatmap(scores_to_matrix(score_sets["TF-IDF"]), title="TF-IDF")

# 문장 비교로 쓰려면 scores만 아래처럼 바꾸면 됩니다.
# score_sets = {
#     "문장 유사도": [
#         ("문장1", "문장2", 0.850),
#         ("문장1", "문장3", 0.120),
#         ("문장2", "문장3", 0.090),
#     ],
# }
