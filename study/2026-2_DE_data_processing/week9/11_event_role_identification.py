"""11. 사건 중심 문장에서 행위자·대상·도구 등 의미역 자동 부착

서술어(동사)를 중심으로 논항을 찾고,
구문 관계·전치사·격 정보를 이용해
Agent, Theme, Instrument 등 의미역을 붙입니다.
능동/수동 문장도 함께 처리합니다.
"""

import spacy

nlp = spacy.load("de_core_news_sm")

# 구문 관계 → 기본 의미역 (능동태 기준)
DEP_TO_ROLE = {
    "sb": "행위자(Agent)",
    "nsubj": "행위자(Agent)",
    "oa": "대상(Theme)",
    "obj": "대상(Theme)",
    "dobj": "대상(Theme)",
    "da": "수혜자(Beneficiary)",
    "iobj": "수혜자(Beneficiary)",
    "sbp": "행위자(Agent)",  # 수동태 von-구의 행위자
}

# 전치사 → 의미역 (도구, 장소, 방향 등)
PREP_TO_ROLE = {
    "mit": "도구(Instrument)",
    "durch": "도구(Instrument)",
    "von": "출발점(Source)",
    "aus": "출발점(Source)",
    "nach": "도착점(Goal)",
    "zu": "도착점(Goal)",
    "für": "수혜자(Beneficiary)",
    "in": "장소(Location)",
    "auf": "장소(Location)",
    "an": "장소(Location)",
    "um": "시간(Time)",
}

# 격 정보로 의미역을 추정할 때의 보조 규칙
CASE_TO_ROLE = {
    "Nom": "행위자(Agent)",
    "Acc": "대상(Theme)",
    "Dat": "수혜자(Beneficiary)",
}

# 출력 시 의미역을 보기 좋은 순서로 정렬하기 위한 목록
ROLE_ORDER = [
    "행위자(Agent)",
    "대상(Theme)",
    "수혜자(Beneficiary)",
    "도구(Instrument)",
    "장소(Location)",
    "출발점(Source)",
    "도착점(Goal)",
    "시간(Time)",
    "부가역(Oblique)",
]


def find_predicates(doc):
    """사건의 중심이 되는 본동사(서술어)를 찾는다."""
    return [token for token in doc if token.pos_ == "VERB"]


def is_passive(predicate):
    """werden + 과거분사 형태의 수동태인지 판별한다."""
    if predicate.head.lemma_ == "werden":
        return True
    return any(child.lemma_ == "werden" and child.pos_ == "AUX"
               for child in predicate.children)


def argument_candidates(predicate):
    """서술어와 관련된 논항 후보를 모은다."""
    candidates = []
    seen = set()

    def add(token):
        # 같은 토큰을 중복으로 넣지 않음
        if token.i not in seen and token != predicate:
            seen.add(token.i)
            candidates.append(token)

    # 서술어의 직접 자식
    for child in predicate.children:
        add(child)

    # 조동사가 문장 핵일 때(수동태 등) 주어를 서술어 쪽으로 가져온다.
    if predicate.head != predicate and predicate.head.pos_ == "AUX":
        for child in predicate.head.children:
            add(child)

    # 목적어에 매달린 전치사구(도구 등)도 사건 참여자로 검토한다.
    nested = [
        grandchild
        for token in list(candidates)
        for grandchild in token.children
        if grandchild.pos_ == "ADP" or grandchild.dep_ in {"mo", "mnr", "sbp"}
    ]
    for token in nested:
        add(token)

    return candidates


def assign_role(token, passive):
    """구문 관계·전치사·격을 이용해 의미역을 부여한다."""
    # 전치사구 / 부가어 처리
    if token.pos_ == "ADP" or token.dep_ in {"mo", "mnr", "sbp", "pg"}:
        prep = token.lemma_.lower()
        # 수동태에서 von/durch는 행위자를 나타냄
        if passive and prep in {"von", "durch"}:
            return "행위자(Agent)"
        if token.dep_ == "sbp":
            return "행위자(Agent)"
        return PREP_TO_ROLE.get(prep, "부가역(Oblique)")

    # 주어: 능동이면 행위자, 수동이면 대상
    if token.dep_ in {"sb", "nsubj"}:
        return "대상(Theme)" if passive else "행위자(Agent)"

    if token.dep_ in DEP_TO_ROLE:
        return DEP_TO_ROLE[token.dep_]

    # 구문 라벨이 애매하면 격 정보로 보조 추정
    case = token.morph.get("Case")
    if case:
        role = CASE_TO_ROLE.get(case[0])
        if role == "행위자(Agent)" and passive:
            return "대상(Theme)"
        return role

    return None


def phrase_of(token, other_args):
    """다른 의미역으로 분리된 하위 구는 제외하고 표면 구를 복원한다.
    예: 'öffnet die Tür mit dem Schlüssel'에서
        'die Tür'와 'mit dem Schlüssel'를 각각 따로 표시.
    """
    own_ids = {t.i for t in token.subtree}
    skip_ids = set()
    for other in other_args:
        if other == token:
            continue
        other_ids = {t.i for t in other.subtree}
        # 다른 논항이 이 구의 하위이면 제외
        if other_ids <= own_ids:
            skip_ids.update(other_ids)
    return "".join(
        t.text_with_ws for t in token.subtree if t.i not in skip_ids
    ).strip()


def label_roles(sentence):
    """문장에 의미역을 자동 부착한다."""
    doc = nlp(sentence)
    events = []

    for predicate in find_predicates(doc):
        passive = is_passive(predicate)
        assigned = []

        for token in argument_candidates(predicate):
            # 명사/대명사/전치사만 의미역 후보로 사용
            if token.pos_ not in {"NOUN", "PROPN", "PRON", "ADP"}:
                continue
            # 구두점, 부정, 분리동사 접두사 등은 제외
            if token.dep_ in {"punct", "oc", "ng", "svp"}:
                continue
            role = assign_role(token, passive)
            if role:
                assigned.append((token, role))

        heads = [token for token, _ in assigned]
        roles = [
            {
                "role": role,
                "phrase": phrase_of(token, heads),
                "dep": token.dep_,
            }
            for token, role in assigned
        ]
        # ROLE_ORDER에 따라 출력 순서 정렬
        roles.sort(key=lambda item: ROLE_ORDER.index(item["role"])
                   if item["role"] in ROLE_ORDER else len(ROLE_ORDER))

        events.append({
            "predicate": predicate.lemma_,
            "surface": predicate.text,
            "passive": passive,
            "roles": roles,
        })

    return events


def print_roles(sentence):
    """의미역 부착 결과를 읽기 쉽게 출력한다."""
    print("문장:", sentence)
    events = label_roles(sentence)
    if not events:
        print("- 서술어를 찾지 못했습니다.")
        print()
        return

    for event in events:
        voice = "수동" if event["passive"] else "능동"
        print(f"서술어(Predicate): {event['surface']} ({event['predicate']}, {voice})")
        for item in event["roles"]:
            print(f"- {item['role']}: {item['phrase']}")
        print()


if __name__ == "__main__":
    # 도구, 수동태, 수혜자, 장소·방향 등 다양한 의미역 예문
    examples = [
        "Der Arzt öffnet die Tür mit dem Schlüssel.",
        "Der Student liest das Buch.",
        "Die Tür wird vom Arzt geöffnet.",
        "Die Mutter gibt dem Kind ein Buch.",
        "Der Lehrer erklärt den Schülern die Grammatik mit der Tafel.",
        "Anna fährt mit dem Zug nach Berlin.",
        "Der Student liest das Buch in der Bibliothek.",
    ]

    for sentence in examples:
        print_roles(sentence)
