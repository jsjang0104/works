"""16. 문자열 표층 유사도 (SequenceMatcher)

핵심 아이디어:
  표층 유사도는 "의미가 비슷한가"가 아니라
  "글자(또는 단어)가 얼마나 겹치는가"를 봅니다.

  SequenceMatcher는 두 문자열에서 연속으로 같은 부분을 찾고,
  그 비율을 0~1 점수로 돌려줍니다.

    ratio = 2 × (겹친 글자 수) / (문장1 길이 + 문장2 길이)

  예) "ABC" 와 "ABD"
      겹친 부분 "AB" (2글자)
      → 2 × 2 / (3 + 3) = 0.667

이 프로그램이 하는 일 (3단계):
  1) 비교할 문장을 준비한다
  2) 문장 쌍마다 SequenceMatcher 점수를 계산한다
  3) 모든 쌍의 점수를 출력한다

입력(texts)만 바꾸면 단어 비교에도, 문장 비교에도 그대로 쓸 수 있습니다.
점수는 13번·14번과 같은 [(이름1, 이름2, 점수), ...] 형식입니다.
"""

# difflib.SequenceMatcher: 파이썬 기본 라이브러리.
# 두 서열(문자열, 목록)이 얼마나 겹치는지 계산합니다.
# 별도 설치가 필요 없습니다.
from difflib import SequenceMatcher


# =====================================================
# 입력 설정
# 직접 손대는 곳은 여기입니다.
# 이름과 문장만 바꾸면 유사도가 자동으로 다시 계산됩니다.
# =====================================================

# 비교할 항목: {이름: 문자열}
# 아래 예는 "글자는 비슷한가"와 "의미는 비슷한가"가
# 어긋날 수 있음을 보여 주기 위해 고른 문장입니다.
texts = {
    "학생-읽기": "Der Student liest ein Buch.",
    "학생-읽기-변형": "Ein Student liest gerade ein Buch.",
    "기차-도착": "Der Zug kommt pünktlich an.",
    "기차-패러프레이즈": "Der Zug erreicht rechtzeitig den Bahnhof.",
    "날씨": "Heute regnet es in Berlin.",
}

# 비교 단위:
#   "char" → 글자 하나하나 (공백·구두점 포함)
#   "word" → 공백으로 나눈 단어 목록
LEVEL = "char"


# =====================================================
# 함수들
# 같은 일을 여러 문장 쌍에 반복하므로, 미리 절차를 함수로 적어 둡니다.
# =====================================================

def prepare_sequence(text, level="char"):
    """비교에 쓸 서열을 만듭니다.

    level="char" 이면 문자열 그대로입니다.
      예) "ein Buch." → 'e','i','n',' ','B',... 글자 단위

    level="word" 이면 공백으로 나눈 단어 목록입니다.
      예) "ein Buch." → ["ein", "Buch."]
      단어 철자가 같아야 겹친 것으로 봅니다.
    """
    if level == "word":
        return text.split()
    return text


def surface_similarity(s1, s2, level="char"):
    """두 문자열의 표층 유사도를 계산합니다. (0~1)

    SequenceMatcher(None, a, b):
      첫 인자 None  → 무시할 글자를 따로 두지 않음
                      (공백·구두점도 비교에 포함)
      .ratio()      → 겹친 비율 (0.0 ~ 1.0)

    1에 가까울수록 글자(또는 단어)가 많이 겹칩니다.
    의미가 비슷한지는 이 점수만으로 알 수 없습니다.
    """
    seq1 = prepare_sequence(s1, level)
    seq2 = prepare_sequence(s2, level)
    return SequenceMatcher(None, seq1, seq2).ratio()


def pairwise_scores(texts, level="char"):
    """모든 항목 쌍의 표층 유사도를 계산합니다.

    자기 자신과의 비교는 넣지 않습니다 (항상 1.0에 가깝기 때문).
    (A, B)만 계산하고 (B, A)는 생략합니다. 같은 점수입니다.

    결과는 [(이름1, 이름2, 점수), ...] 목록입니다.
    18번 Heatmap에 그대로 넣을 수 있는 형식입니다.
    """
    names = list(texts.keys())
    pairs = []
    for i, name1 in enumerate(names):
        # i+1부터 보면 같은 쌍을 두 번 계산하지 않습니다.
        for name2 in names[i + 1:]:
            score = surface_similarity(texts[name1], texts[name2], level)
            pairs.append((name1, name2, score))
    return pairs


# =====================================================
# 실행 부분: 위에서 만든 함수를 실제로 순서대로 호출합니다.
# =====================================================

print("1) 비교할 문장")
print(f"   비교 단위: {LEVEL}  (char=글자, word=단어)")
for name, text in texts.items():
    print(f"- {name}")
    print(f"  {text}")
print("-" * 50)


print("2) 표층 유사도 (SequenceMatcher)")
print("   1에 가까울수록 글자(또는 단어)가 많이 겹칩니다.")
print("   의미가 비슷한 것과는 다를 수 있습니다.")
scores = pairwise_scores(texts, level=LEVEL)
for name1, name2, score in scores:
    print(f"- {name1} - {name2}: {score:.3f}")
print("-" * 50)

# 이 예에서 대략 이렇게 나와야 합니다.
#   학생-읽기 - 학생-읽기-변형 : 높음
#       단어가 거의 같고, 글자도 많이 겹칩니다.
#   기차-도착 - 기차-패러프레이즈 : 낮거나 중간
#       의미는 비슷하지만 단어(kommt/erreicht, pünktlich/rechtzeitig)가 다릅니다.
#   학생-읽기 - 날씨 : 낮음
#       글자도 의미도 다릅니다.

# 단어 단위로 보려면 LEVEL만 바꾸면 됩니다.
# LEVEL = "word"

# 문장을 바꾸고 싶다면 texts만 아래처럼 바꾸면 됩니다.
# texts = {
#     "문장1": "Ich lese ein Buch.",
#     "문장2": "Ich studiere Germanistik.",
#     "문장3": "Das Wetter ist schön.",
# }
