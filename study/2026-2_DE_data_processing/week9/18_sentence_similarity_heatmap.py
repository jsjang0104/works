"""18. 문장 유사도 점수 Heatmap (일반화)

핵심 아이디어:
  16번(표층, SequenceMatcher)과 17번(의미, 임베딩)은 문장 쌍의 유사도를
  아래와 같은 목록으로 남깁니다.

      scores = [(이름1, 이름2, 점수), (이름1, 이름3, 점수), ...]

  Heatmap은 "누가 누구와 얼마나 비슷한가"를 색으로 보여 줍니다.
  그러려면 쌍 목록을 정사각 행렬로 바꿔야 합니다.

      행렬[i, j] = i번째 문장과 j번째 문장의 유사도
      대각선(자기 자신)은 항상 1.0
      (A, B)와 (B, A)는 같은 점수입니다 (대칭).

  표층 점수와 의미 점수를 나란히 그리면,
  "글자는 다른데 뜻은 비슷한" 패러프레이즈가 잘 보입니다.

이 프로그램이 하는 일 (3단계):
  1) scores에서 문장 이름을 모은다
  2) 이름 × 이름 정사각 행렬을 만든다
  3) 행렬을 heatmap으로 그린다

16번 scores든 17번 scores든, 같은 함수에 넣으면 됩니다.
문장 수·이름·점수 계산 방법이 바뀌어도 입력 형식만 지키면 됩니다.
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
    mpl.rcParams["axes.unicode_minus"] = False  # 마이너스 기호가 네모로 깨지지 않게


# =====================================================
# 입력 설정
# 직접 손대는 곳은 여기입니다.
# 16번·17번이 만든 scores를 그대로 넣으면 heatmap이 그려집니다.
# 여러 개를 넣으면 나란히 비교합니다.
# =====================================================

# 이름 → 원문. heatmap 칸의 짧은 이름을 해석할 때 참고합니다.
# 점수를 바꿀 필요는 없고, 출력 설명용입니다.
texts = {
    "학생-읽기": "Der Student liest ein Buch.",
    "학생-읽기-변형": "Ein Student liest gerade ein Buch.",
    "기차-도착": "Der Zug kommt pünktlich an.",
    "기차-패러프레이즈": "Der Zug erreicht rechtzeitig den Bahnhof.",
    "날씨": "Heute regnet es in Berlin.",
}

# 각 값은 16번, 17번의 pairwise_scores()와 같은 형식입니다.
#   [(이름1, 이름2, 점수), ...]
# 자기 자신과의 쌍은 넣지 않아도 됩니다. 행렬을 만들 때 1.0으로 채웁니다.
#
# 아래 숫자는 16번·17번을 기본 문장으로 실행했을 때의 결과입니다.
# 문장을 바꿨다면, 그 프로그램이 출력한 점수를 여기로 옮겨 적으면 됩니다.
score_sets = {
    "표층 유사도 (SequenceMatcher)": [
        ("학생-읽기", "학생-읽기-변형", 0.787),
        ("학생-읽기", "기차-도착", 0.444),
        ("학생-읽기", "기차-패러프레이즈", 0.353),
        ("학생-읽기", "날씨", 0.491),
        ("학생-읽기-변형", "기차-도착", 0.295),
        ("학생-읽기-변형", "기차-패러프레이즈", 0.267),
        ("학생-읽기-변형", "날씨", 0.400),
        ("기차-도착", "기차-패러프레이즈", 0.441),
        ("기차-도착", "날씨", 0.226),
        ("기차-패러프레이즈", "날씨", 0.418),
    ],
    "의미 유사도 (임베딩)": [
        ("학생-읽기", "학생-읽기-변형", 0.986),
        ("학생-읽기", "기차-도착", 0.012),
        ("학생-읽기", "기차-패러프레이즈", -0.011),
        ("학생-읽기", "날씨", -0.060),
        ("학생-읽기-변형", "기차-도착", 0.020),
        ("학생-읽기-변형", "기차-패러프레이즈", -0.009),
        ("학생-읽기-변형", "날씨", -0.042),
        ("기차-도착", "기차-패러프레이즈", 0.937),
        ("기차-도착", "날씨", 0.211),
        ("기차-패러프레이즈", "날씨", 0.213),
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
      [("학생-읽기", "날씨", 0.49), ("기차-도착", "날씨", 0.23)]
      → ["학생-읽기", "날씨", "기차-도착"]

    순서를 고정해야 행과 열의 칸이 같은 문장을 가리킵니다.
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
      1) [(이름1, 이름2, 점수), ...]   ← 16번, 17번
      2) 이미 정사각인 DataFrame       ← 그대로 돌려줌

    만드는 방법:
      - 대각선(같은 이름끼리)은 self_score (기본 1.0)
      - (A, B) 점수는 (B, A)에도 같은 값으로 넣음 (대칭)
      - 목록에 없는 쌍은 0.0

    예)
      scores = [("학생-읽기", "학생-읽기-변형", 0.787)]
      →
                         학생-읽기  학생-읽기-변형
        학생-읽기            1.000          0.787
        학생-읽기-변형       0.787          1.000
    """
    # 이미 표(행렬)로 들어온 경우에는 다시 만들 필요가 없습니다.
    if isinstance(scores, pd.DataFrame):
        return scores

    if names is None:
        names = collect_names(scores)

    # 먼저 모든 칸을 0.0으로 만들어 둡니다.
    matrix = pd.DataFrame(0.0, index=names, columns=names)

    # 자기 자신과의 유사도는 1.0입니다 (같은 문장).
    for name in names:
        matrix.loc[name, name] = self_score

    # 쌍 점수를 위·아래 삼각형에 같이 넣습니다.
    # loc[행, 열] = 값  → 표에서 그 칸을 찾아 숫자를 넣습니다.
    for name1, name2, score in scores:
        matrix.loc[name1, name2] = score
        matrix.loc[name2, name1] = score

    return matrix


def draw_heatmap(matrix, title="유사도 Heatmap", ax=None, cmap="YlGnBu"):
    """한 장의 유사도 행렬을 heatmap으로 그립니다.

    annot=True : 칸 안에 숫자도 같이 보여 줍니다.
    vmin~vmax  : 색 눈금을 0~1로 고정합니다.
                 (표층 점수와 의미 점수를 같은 색 기준으로 비교하기 쉽습니다.)
    square     : 칸을 정사각형으로 만들어, 표처럼 보이게 합니다.
    """
    created_fig = ax is None
    if created_fig:
        n = len(matrix)
        # 문장 이름이 길어서, 칸이 너무 작아지지 않게 크기를 조금 키웁니다.
        plt.figure(figsize=(max(6.0, n * 1.6), max(5.0, n * 1.4)))
        ax = plt.gca()  # 지금 그림의 좌표축을 가져옵니다.

    sns.heatmap(
        matrix,
        annot=True,      # 칸 안에 점수 표시
        fmt=".3f",       # 16번·17번 print와 같은 소수점 세 자리
        cmap=cmap,       # 색상표. 값이 클수록 진한 파란색
        vmin=0,
        vmax=1,
        square=True,     # 칸을 정사각형으로
        ax=ax,
    )
    ax.set_title(title)
    # 가로축 이름이 겹치지 않게 기울입니다.
    ax.tick_params(axis="x", labelrotation=40)
    ax.tick_params(axis="y", labelrotation=0)

    if created_fig:
        plt.tight_layout()
        plt.show()


def draw_score_sets(score_sets, cmap="YlGnBu"):
    """여러 scores를 받아 heatmap을 그립니다.

    1개면 한 장, 2개 이상이면 나란히 그립니다.
    16번과 17번을 같이 넣으면 표층/의미 점수 차이를 바로 볼 수 있습니다.
    """
    items = list(score_sets.items())  # [("제목", scores), ...]
    n = len(items)
    if n == 0:
        raise ValueError("score_sets가 비어 있습니다.")

    # 항목이 많아져도 칸이 너무 작아지지 않게, 그림 크기를 이름 수에 맞춥니다.
    first_scores = items[0][1]
    if isinstance(first_scores, pd.DataFrame):
        sample_names = list(first_scores.index)
    else:
        sample_names = collect_names(first_scores)
    cell = max(6.0, len(sample_names) * 1.6)

    # 1행 n열: 표층 heatmap | 의미 heatmap 처럼 가로로 붙입니다.
    fig, axes = plt.subplots(1, n, figsize=(cell * n, cell))
    if n == 1:
        # subplots를 1개만 만들면 axes가 목록이 아니라 하나만 옵니다.
        # 아래 for문이 항상 목록을 돌도록 맞춰 둡니다.
        axes = [axes]

    for ax, (title, scores) in zip(axes, items):
        matrix = scores_to_matrix(scores)
        draw_heatmap(matrix, title=title, ax=ax, cmap=cmap)

    fig.suptitle("문장 유사도 Heatmap", y=1.02)
    plt.tight_layout()
    plt.show()


# =====================================================
# 실행 부분: 위에서 만든 함수를 실제로 순서대로 호출합니다.
# =====================================================

print("1) 비교할 문장")
print("   heatmap 칸의 짧은 이름은 아래 문장을 가리킵니다.")
for name, text in texts.items():
    print(f"- {name}")
    print(f"  {text}")
print("-" * 50)


print("2) 쌍 목록 → 정사각 행렬")
print("   대각선은 1.000, (A,B)와 (B,A)는 같은 값입니다.")
for title, scores in score_sets.items():
    matrix = scores_to_matrix(scores)
    print(f"\n- {title}")
    print(matrix.round(3).to_string())
print("-" * 50)


print("3) Heatmap")
print("   색이 진할수록 두 문장이 더 비슷합니다.")
print("   표층: 글자(또는 단어)가 겹치는 정도")
print("   의미: 임베딩이 보기에 뜻이 비슷한 정도")
print("   기차-도착 / 기차-패러프레이즈 칸을 두 그림에서 비교해 보세요.")
print("   → 표층은 중간, 의미는 높음 (단어는 달라도 사건이 비슷함)")
draw_score_sets(score_sets)
print("-" * 50)

# 하나만 그리고 싶다면 아래처럼 쓰면 됩니다.
# draw_heatmap(
#     scores_to_matrix(score_sets["표층 유사도 (SequenceMatcher)"]),
#     title="표층 유사도",
# )
# draw_heatmap(
#     scores_to_matrix(score_sets["의미 유사도 (임베딩)"]),
#     title="의미 유사도",
# )

# 문장이나 점수를 바꾸고 싶다면 score_sets만 아래처럼 바꾸면 됩니다.
# 16번·17번을 실행한 뒤, 출력된 숫자를 그대로 옮기면 됩니다.
# score_sets = {
#     "표층 유사도 (SequenceMatcher)": [
#         ("문장1", "문장2", 0.850),
#         ("문장1", "문장3", 0.120),
#         ("문장2", "문장3", 0.090),
#     ],
#     "의미 유사도 (임베딩)": [
#         ("문장1", "문장2", 0.910),
#         ("문장1", "문장3", 0.080),
#         ("문장2", "문장3", 0.050),
#     ],
# }
