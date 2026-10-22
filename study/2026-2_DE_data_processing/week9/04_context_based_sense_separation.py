"""04. 문맥에 따른 의미 후보 분리

핵심 아이디어:
  같은 단어라도 옆에 오는 단어가 다르면 의미가 다를 수 있습니다.
  예) Bank + Geld  → 금융기관
      Bank + Park  → 벤치

이 프로그램이 하는 일 (4단계):
  1) 각 문장에서 의미 단서가 되는 문맥 단어를 꺼낸다
  2) 문맥 단어가 겹치는 문장끼리 같은 의미 후보로 묶는다
  3) 각 묶음의 특징 단어(sense_keywords)를 자동으로 만든다
  4) 키워드가 얼마나 겹치는지로 문장의 의미를 예측한다
"""

# re: 정규표현식 모듈. 문장에서 단어만 골라 낼 때 사용합니다.
import re

# =====================================================
# 입력 설정
# 직접 손대는 곳은 여기입니다.
# 다른 다의어를 보려면 target_word와 sentences만 바꾸면 됩니다.
# =====================================================

# 의미를 나누고 싶은 다의어
target_word = "Bank"

# 이 문장들로부터 의미 묶음과 키워드를 자동으로 만듭니다.
# (같은 단어 Bank가 쓰였지만, 앞뒤 단어가 다릅니다.)
sentences = [
    "Ich gehe zur Bank, um Geld abzuheben.",   # 돈을 찾으러 가다 → 금융 쪽 문맥
    "Die Bank zahlt das Geld auf mein Konto.", # 계좌에 돈을 넣다 → 금융 쪽 문맥
    "Ich brauche Geld und gehe zur Bank.",     # 돈이 필요하다 → 금융 쪽 문맥
    "Wir sitzen auf der Bank im Park.",        # 공원에 앉다 → 벤치 쪽 문맥
    "Die Bank im Park ist nass.",              # 공원의 벤치가 젖다 → 벤치 쪽 문맥
    "Wir sitzen auf einer Bank unter dem Baum.",  # 나무 아래 앉다 → 벤치 쪽 문맥
]

# 키워드를 만든 다음에, 아직 묶음에 넣지 않은 새 문장도 같은 방식으로 판별합니다.
extra_sentences = [
    "Sie hat bei der Bank ein Konto.",                    # Konto가 있으면 금융 쪽으로 예측
    "Die Kinder sitzen auf der Bank unter dem Baum.",     # sitzen, Baum이 있으면 벤치 쪽으로 예측
]

# 프로그램은 일단 묶음 이름을 의미1, 의미2처럼 번호로 붙입니다.
# 키워드를 보고 사람이 "아, 이건 금융기관이구나"라고 이름을 다는 칸입니다.
# 이 딕셔너리를 {} 로 비워 두면 의미1, 의미2가 그대로 출력됩니다.
sense_rename = {
    "의미1": "금융기관",
    "의미2": "벤치",
}

# 불용어: 거의 모든 문장에 나와서 의미 구분에 도움이 안 되는 단어
# 예) der, die, und, ist 는 금융 문장이든 벤치 문장이든 다 나옵니다.
# 소문자로 적어 두고, 비교할 때도 소문자로 맞춰 봅니다.
STOPWORDS = {
    "ich", "du", "er", "sie", "es", "wir", "ihr", "man",
    "der", "die", "das", "den", "dem", "des",
    "ein", "eine", "einer", "einem", "einen", "eines",
    "und", "oder", "aber", "um", "zu", "zur", "zum",
    "auf", "in", "im", "an", "am", "unter", "über",
    "vor", "von", "mit", "für", "aus", "nach", "bei",
    "ist", "sind", "war", "hat", "haben", "wird", "werden",
    "kann", "muss", "mein", "meine", "sein", "seine",
    "gehe", "geht", "gehen",  # "가다"는 너무 흔해서 단서로 쓰지 않음
}


# =====================================================
# 함수들
# 같은 일을 여러 문장에 반복하므로, 미리 절차를 함수로 적어 둡니다.
# =====================================================

def tokenize(sentence):
    """문장을 단어 목록으로 쪼갭니다.

    예) "Wir sitzen auf der Bank im Park."
     → ["Wir", "sitzen", "auf", "der", "Bank", "im", "Park"]

    쉼표·마침표 같은 구두점은 버리고,
    독일어 알파벳(Ä Ö Ü ß 포함)으로 된 덩어리만 단어로 봅니다.
    """
    return re.findall(r"[A-Za-zÄÖÜäöüß]+", sentence)


def context_words(sentence, target_word, stopwords=STOPWORDS):
    """의미 단서가 되는 문맥 단어만 남깁니다.

    빼는 것:
      1) 대상 단어 자체 (Bank) → 모든 문장에 있으므로 구분에 쓸모가 없음
      2) 불용어 (der, und, ist ...) → 너무 흔해서 단서가 안 됨

    예) "Ich gehe zur Bank, um Geld abzuheben."
     → {"Geld", "abzuheben"}
    """
    target = target_word.lower()  # Bank / bank 를 같게 보기 위해 소문자로
    words = set()  # set: 같은 단어는 한 번만 담는 집합

    for token in tokenize(sentence):
        lowered = token.lower()
        # 대상 단어이거나 불용어이면 건너뜁니다 (continue = 아래 줄 실행 안 함)
        if lowered == target or lowered in stopwords:
            continue
        words.add(token)  # 남은 단어만 문맥 단서로 저장

    return words


def group_similar_contexts(contexts, min_overlap=1):
    """문맥 단어가 겹치는 문장들을 같은 의미 후보로 묶습니다.

    생각 방법:
      "Geld"가 있는 문장끼리는 서로 이어지고,
      "Park"/"sitzen"이 있는 문장끼리는 따로 이어집니다.
      그래서 자연스럽게 두 묶음이 생깁니다.

    min_overlap=1 은 "공통 단어가 1개 이상이면 같은 묶음"이라는 뜻입니다.
    """
    n = len(contexts)          # 문장 개수
    assigned = [-1] * n        # 아직 아무 묶음에도 안 넣었으면 -1
    groups = []                # 완성된 묶음들을 담을 목록

    for i in range(n):
        # 이미 다른 묶음에 들어간 문장은 건너뜁니다
        if assigned[i] != -1:
            continue

        # i번 문장에서 새 묶음을 시작합니다
        bundle = [i]
        assigned[i] = len(groups)  # 이 문장의 묶음 번호 기록
        changed = True

        # 묶음에 새 문장이 더해지는 동안 계속 반복합니다
        while changed:
            changed = False

            # 지금 묶음에 있는 모든 문맥 단어를 한 덩어리로 합칩니다
            # 예) {Geld} ∪ {Geld, Konto} → {Geld, Konto}
            bundle_words = set()
            for j in bundle:
                bundle_words |= contexts[j]  # |= 는 합집합(union)

            # 아직 안 넣은 문장 중에서, 공통 단어가 있는 문장을 찾아 넣습니다
            for k in range(n):
                overlap = len(bundle_words & contexts[k])  # & 는 교집합(겹치는 단어)
                if assigned[k] == -1 and overlap >= min_overlap:
                    bundle.append(k)
                    assigned[k] = len(groups)
                    changed = True  # 새 문장이 들어왔으니 한 번 더 살펴봄

        # 묶음 안 문장 번호를 작은 숫자부터 정렬해 저장
        groups.append(sorted(bundle))

    return groups


def build_sense_keywords(contexts, groups):
    """각 묶음을 대표하는 특징 단어(sense_keywords)를 만듭니다.

    특징 단어 = "이 묶음에는 나오지만 다른 묶음에는 잘 안 나오는 단어"
    예) 금융 묶음: Geld, Konto, abzuheben
        벤치 묶음: Park, sitzen, Baum

    집합에서 빼기(-)를 쓰면 "우리만 가진 단어"를 바로 구할 수 있습니다.
    """
    # 묶음마다 문맥 단어를 모두 합쳐 둡니다
    words_by_group = []
    for indexes in groups:
        words = set()
        for i in indexes:
            words |= contexts[i]
        words_by_group.append(words)

    sense_keywords = {}  # {의미이름: 키워드 집합}

    for g, words in enumerate(words_by_group):
        # enumerate: 0부터 번호를 붙여 가며 꺼냄 (g=0, 1, 2, ...)
        others = set()
        for h, other_words in enumerate(words_by_group):
            if h != g:  # 지금 묶음이 아닌 나머지
                others |= other_words

        # 우리 단어 - 남 단어 = 우리만의 단서 단어
        distinctive = words - others

        # 혹시 공통 단어만 있으면(우리만의 단어가 없으면) 묶음 단어 전체를 사용
        sense_keywords[f"의미{g + 1}"] = distinctive if distinctive else words

    return sense_keywords


def score_senses(sentence, sense_keywords, target_word, stopwords=STOPWORDS):
    """문장의 문맥 단어와 의미별 키워드가 몇 개나 겹치는지 셉니다.

    예) 문맥 = {Geld, abzuheben}
        금융기관 키워드 = {Geld, Konto, abzuheben}  → 겹침 2
        벤치 키워드     = {Park, sitzen}            → 겹침 0
    """
    tokens = context_words(sentence, target_word, stopwords)
    scores = {}
    for sense, keywords in sense_keywords.items():
        scores[sense] = len(tokens & keywords)  # 겹치는 단어 개수 = 점수
    return scores


def predict_sense(scores):
    """점수가 가장 높은 의미를 예측값으로 고릅니다.

    판단 불가가 되는 경우:
      - 모든 점수가 0 (키워드가 하나도 안 겹침)
      - 1등이 두 개 이상 (동점)
    """
    if not scores or max(scores.values()) == 0:
        return "판단 불가"

    best = max(scores.values())  # 가장 높은 점수
    # 최고점을 받은 의미가 여러 개일 수 있으므로 목록으로 모읍니다
    winners = [sense for sense, score in scores.items() if score == best]

    if len(winners) > 1:
        return "판단 불가"
    return winners[0]


# =====================================================
# 실행 부분: 위에서 만든 함수를 실제로 순서대로 호출합니다.
# =====================================================

# 1) 각 문장에서 문맥 단어를 꺼냅니다
contexts = [context_words(sentence, target_word) for sentence in sentences]

print("문맥 단어 추출")
print("(대상 단어 Bank와 불용어를 뺀 나머지입니다)")
for sentence, words in zip(sentences, contexts):
    # zip: 문장과 문맥 단어를 짝지어 함께 꺼냅니다
    print(f"- {sentence}")
    print(f"  문맥: {words if words else '{}'}")
print("-" * 40)


# 2) 문맥이 비슷한 문장끼리 묶습니다
groups = group_similar_contexts(contexts)

print("의미 후보 묶음")
print("(겹치는 문맥 단어가 있는 문장끼리 모았습니다)")
for g, indexes in enumerate(groups):
    # 사람이 붙인 이름이 있으면 그것을, 없으면 의미1, 의미2를 사용
    label = sense_rename.get(f"의미{g + 1}", f"의미{g + 1}")
    print(f"[{label}]")
    for i in indexes:
        print(f"  - {sentences[i]}")
print("-" * 40)


# 3) 묶음별 특징 단어 = sense_keywords 를 자동으로 만듭니다
sense_keywords = build_sense_keywords(contexts, groups)

# 의미1, 의미2 를 금융기관, 벤치처럼 읽기 쉬운 이름으로 바꿉니다
renamed = {}
for sense, keywords in sense_keywords.items():
    new_name = sense_rename.get(sense, sense)  # 이름이 없으면 원래 이름 유지
    renamed[new_name] = keywords
sense_keywords = renamed

print("자동 생성 sense_keywords")
print("(한 묶음에만 나타나는 단어를 그 의미의 단서로 씁니다)")
for sense, keywords in sense_keywords.items():
    print(f"- {sense}: {keywords}")
print("-" * 40)


# 4) 만든 키워드로 각 문장의 의미를 예측합니다
print("의미 예측")
print("(문장 단어 ∩ 키워드 개수가 더 큰 쪽을 선택합니다)")
for sentence in sentences + extra_sentences:  # + 로 두 목록을 이어 붙임
    scores = score_senses(sentence, sense_keywords, target_word)
    predicted = predict_sense(scores)
    print(f"문장: {sentence}")
    print("점수:", scores)
    print("예측 의미:", predicted)
    print("-" * 40)

# 다른 다의어에도 target_word와 sentences만 바꾸면 그대로 적용됩니다.
# 예: target_word = "Schloss"  (성 / 자물쇠)
# sentences = [
#     "Das Schloss auf dem Hügel ist alt.",
#     "Wir besichtigen das Schloss in der Stadt.",
#     "Er öffnet das Schloss mit einem Schlüssel.",
#     "Das Schloss der Tür ist kaputt.",
# ]
