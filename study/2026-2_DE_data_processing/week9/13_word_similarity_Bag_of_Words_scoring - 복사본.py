"""13. 단어 의미 유사도 계산 및 점수 비교

핵심 아이디어:
  단어의 의미는 "그 단어가 어떤 단어들과 함께 나타나는가"로 대략 잡을 수 있습니다.
  예) Haus / Gebäude 옆에는 Dach, Fenster, Tür 가 자주 나옵니다.
      Baum 옆에는 Park, Blätter, Äste 가 자주 나옵니다.

Bag-of-Words (단어 주머니):
  텍스트를 가방에 단어를 담듯이 표현합니다.
  순서는 버리고, "어떤 단어가 몇 번 나왔는가"만 셉니다.
  그 빈도 목록이 곧 벡터(숫자 목록)가 됩니다.

이 프로그램이 하는 일 (4단계):
  1) 각 항목의 텍스트에서 단어를 꺼낸다 (토큰화)
  2) 모든 텍스트를 모아 어휘 목록(vocabulary)을 만든다
  3) 어휘 순서에 맞춰 단어 빈도를 세어 벡터를 만든다
  4) 코사인 유사도로 항목 쌍이 얼마나 비슷한지 계산한다

입력만 바꾸면 단어 비교에도, 문장 비교에도 그대로 쓸 수 있습니다.
"""

# re: 정규표현식. 문장에서 알파벳 덩어리(단어)만 고를 때 사용합니다.
# math.sqrt: 제곱근. 벡터의 길이(크기)를 구할 때 사용합니다.
import re
from math import sqrt

# =====================================================
# 입력 설정
# 직접 손대는 곳은 여기입니다.
# 이름과 텍스트만 바꾸면 벡터와 유사도가 자동으로 다시 계산됩니다.
# =====================================================

# 비교할 항목: {이름: 그 항목을 설명하는 텍스트}
# 여기서는 단어의 "주변 문맥"을 Bag-of-Words 벡터로 씁니다.
# (나중에 문장 유사도를 보려면 이름을 문장으로, 텍스트도 그 문장으로 두면 됩니다.)
texts = {
    "Haus": (
        "Das Haus ist ein Gebäude mit einem Dach. "
        "Menschen wohnen im Haus. Das Haus hat Fenster und eine Tür."
    ),
    "Gebäude": (
        "Ein Gebäude ist groß. Das Haus ist ein Gebäude. "
        "Das Gebäude hat ein Dach, Fenster und eine Tür."
    ),
    "Baum": (
        "Der Baum steht im Park. Der Baum hat grüne Blätter und Äste. "
        "Vögel sitzen auf dem Baum."
    ),
}

# 불용어: 거의 모든 문장에 나와서 의미 비교에 도움이 안 되는 단어
# 예) der, und, ist 는 Haus 텍스트에도 Baum 텍스트에도 나옵니다.
# 소문자로 적어 두고, 비교할 때도 소문자로 맞춥니다.
STOPWORDS = {
    "ich", "du", "er", "sie", "es", "wir", "ihr", "man",
    "der", "die", "das", "den", "dem", "des",
    "ein", "eine", "einer", "einem", "einen", "eines",
    "und", "oder", "aber", "um", "zu", "zur", "zum",
    "auf", "in", "im", "an", "am", "unter", "über",
    "vor", "von", "mit", "für", "aus", "nach", "bei",
    "ist", "sind", "war", "hat", "haben", "wird", "werden",
    "kann", "muss", "mein", "meine", "sein", "seine",
}


# =====================================================
# 함수들
# 같은 일을 여러 텍스트에 반복하므로, 미리 절차를 함수로 적어 둡니다.
# =====================================================

def tokenize(text):
    """텍스트를 단어 목록으로 쪼갭니다.

    예) "Das Haus hat ein Dach."
     → ["Das", "Haus", "hat", "ein", "Dach"]

    쉼표·마침표 같은 구두점은 버리고,
    독일어 알파벳(Ä Ö Ü ß 포함)으로 된 덩어리만 단어로 봅니다.
    """
    return re.findall(r"[A-Za-zÄÖÜäöüß]+", text)


def content_words(text, stopwords=STOPWORDS):
    """의미 비교에 쓸 내용어만 남깁니다.

    하는 일:
      1) 단어를 소문자로 맞춘다  (Haus / haus 를 같게 보기 위해)
      2) 불용어는 버린다         (der, und, ist ...)

    예) "Das Haus hat ein Dach."
     → ["haus", "dach"]
    """
    words = []
    for token in tokenize(text):
        lowered = token.lower()
        if lowered in stopwords:
            continue  # 불용어이면 아래 줄을 실행하지 않고 다음 단어로
        words.append(lowered)
    return words


def build_vocabulary(texts, stopwords=STOPWORDS):
    """모든 텍스트에 나온 단어를 모아 어휘 목록을 만듭니다.

    어휘 목록 = 벡터의 '축' 이름입니다.
    예) ["äste", "baum", "blätter", "dach", "fenster", ...]

    같은 어휘 순서를 모든 벡터가 공유해야
    "3번째 칸은 언제나 dach의 빈도"처럼 칸 의미가 같아집니다.
    sorted()로 가나다(알파벳) 순서를 고정합니다.
    """
    vocab = set()  # set: 같은 단어는 한 번만 담는 집합
    for text in texts.values():
        vocab.update(content_words(text, stopwords))  # update: 여러 개를 한꺼번에 추가
    return sorted(vocab)


def text_to_vector(text, vocabulary, stopwords=STOPWORDS):
    """한 텍스트를 Bag-of-Words 벡터(숫자 목록)로 바꿉니다.

    생각 방법:
      vocabulary = ["dach", "fenster", "park"]
      텍스트에 dach 1번, fenster 1번, park 0번
      → 벡터     = [1,      1,         0]

    각 칸의 숫자는 "그 단어가 몇 번 나왔는가"입니다.
    """
    words = content_words(text, stopwords)

    # 먼저 모든 칸을 0으로 만들어 둡니다.
    counts = {}
    for word in vocabulary:
        counts[word] = 0

    # 실제로 나온 단어만 횟수를 1씩 올립니다.
    for word in words:
        if word in counts:
            counts[word] += 1

    # 딕셔너리(단어→횟수)를 어휘 순서의 숫자 목록으로 바꿉니다.
    vector = [counts[word] for word in vocabulary]
    return vector, counts


def cosine(a, b):
    """두 벡터의 코사인 유사도를 계산합니다.

    공식:  cos(a, b) = (a·b) / (|a| × |b|)

      a·b  : 내적. 같은 위치의 숫자를 곱한 뒤 모두 더함
      |a|  : a의 길이(크기). 각 숫자를 제곱해 더한 뒤 제곱근
      결과 : -1 ~ 1 사이. 텍스트 빈도는 0 이상이라 보통 0 ~ 1

    1에 가까울수록 두 벡터의 방향이 같고, 내용어가 비슷하다는 뜻입니다.
    0에 가까울수록 겹치는 단어가 거의 없습니다.
    """
    # zip: 두 목록에서 같은 위치의 값을 짝지어 꺼냅니다.
    # 예) a=[1, 2], b=[3, 4] → (1,3), (2,4)
    dot = sum(x * y for x, y in zip(a, b))  # 내적
    na = sqrt(sum(x * x for x in a))        # a의 길이
    nb = sqrt(sum(y * y for y in b))        # b의 길이

    # 길이가 0이면 나눌 수 없습니다 (단어가 하나도 안 남은 경우).
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def pairwise_scores(vectors):
    """모든 항목 쌍의 코사인 유사도를 계산합니다.

    자기 자신과의 유사도는 1.0에 가깝습니다 (같은 벡터).
    결과는 [(이름1, 이름2, 점수), ...] 목록입니다.
    """
    names = list(vectors.keys())
    pairs = []
    for i, name1 in enumerate(names):
        # i+1부터 보면 (A,B)와 (B,A)를 중복해서 계산하지 않습니다.
        for name2 in names[i + 1:]:
            score = cosine(vectors[name1], vectors[name2])
            pairs.append((name1, name2, score))
    return pairs


# =====================================================
# 실행 부분: 위에서 만든 함수를 실제로 순서대로 호출합니다.
# =====================================================

# 1) 모든 텍스트를 보고 어휘 목록(벡터의 축)을 만듭니다.
vocabulary = build_vocabulary(texts)

print("1) 어휘 목록 (vocabulary)")
print("   각 칸이 벡터의 한 차원이 됩니다.")
print("  ", vocabulary)
print("-" * 50)


# 2) 항목마다 Bag-of-Words 벡터를 만듭니다.
vectors = {}   # {이름: 숫자 목록}
count_maps = {}  # {이름: {단어: 횟수}}  → 사람이 읽기 쉬운 형태

print("2) Bag-of-Words 벡터")
for name, text in texts.items():
    vector, counts = text_to_vector(text, vocabulary)
    vectors[name] = vector
    count_maps[name] = counts

    # 0이 아닌 칸만 보여 주면, 어떤 단어가 벡터를 만드는지 잘 보입니다.
    used = {word: n for word, n in counts.items() if n > 0}
    print(f"- {name}")
    print(f"  텍스트: {text}")
    print(f"  나온 단어: {used}")
    print(f"  벡터: {vector}")
print("-" * 50)


# 3) 모든 쌍의 코사인 유사도를 계산합니다.
print("3) 코사인 유사도")
print("   1에 가까울수록 내용어가 비슷합니다.")
scores = pairwise_scores(vectors)
for name1, name2, score in scores:
    print(f"- {name1} - {name2}: {score:.3f}")
print("-" * 50)

# 이 예에서는 대략 이렇게 나와야 합니다.
#   Haus - Gebäude : 높음  (Dach, Fenster, Tür, Haus, Gebäude 가 겹침)
#   Haus - Baum    : 낮음  (Park, Blätter 쪽 단어는 거의 안 겹침)
#   Gebäude - Baum : 낮음

# 문장 비교로 쓰려면 texts만 아래처럼 바꾸면 됩니다.
# texts = {
#     "문장1": "Der Student liest ein Buch.",
#     "문장2": "Ein Student liest gerade ein Buch.",
#     "문장3": "Heute regnet es in Berlin.",
# }
