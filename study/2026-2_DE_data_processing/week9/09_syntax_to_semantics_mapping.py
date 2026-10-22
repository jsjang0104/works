"""09. 구문 분석 결과를 의미 해석과 연결

spaCy 의존 구문 분석(dependency parse) 결과를
의미역(행위자, 대상, 수혜자 등)으로 매핑합니다.
구문 관계 라벨 → 의미 역할로 이어지는 과정을 관찰합니다.
"""

import spacy

nlp = spacy.load("de_core_news_sm")

# 구문 관계(dependency) → 의미역
# 독일어 spaCy 모델은 TIGER 체계(sb, oa, da ...)를 쓰며,
# UD 체계(nsubj, obj, iobj ...)도 함께 대응한다.
semantic_map = {
    "sb": "행위자(Agent)",       # TIGER: Subjekt
    "nsubj": "행위자(Agent)",    # UD: nominal subject
    "oa": "대상(Theme)",         # TIGER: Akkusativobjekt
    "obj": "대상(Theme)",        # UD: object
    "dobj": "대상(Theme)",       # UD(구모델): direct object
    "da": "수혜자(Beneficiary)", # TIGER: Dativobjekt
    "iobj": "수혜자(Beneficiary)",
    "mo": "부가어(Modifier)",    # TIGER: Modifikator
    "mnr": "부가어(Modifier)",
    "op": "부가어(Modifier)",
    "obl": "부가어(Modifier)",    # UD: oblique
}


def phrase_of(token):
    """의존 하위 트리를 모아 구(phrase)를 복원한다.
    예: 'das Buch' 전체를 하나의 구성요소로 가져옴.
    """
    return "".join(t.text_with_ws for t in token.subtree).strip()


def parse_syntax(sentence):
    """의존 파싱으로 (구성요소, 구문관계, 중심어) 목록을 만든다.
    동사(또는 조동사)에 직접 매달린 의미역 후보만 수집한다.
    """
    doc = nlp(sentence)
    syntax = []
    for token in doc:
        # 의미역으로 매핑할 수 있는 구문 관계만 사용
        if token.dep_ not in semantic_map:
            continue
        # 중심어가 동사/조동사인 경우만 (서술어 논항)
        if token.head.pos_ not in {"VERB", "AUX"}:
            continue
        syntax.append((phrase_of(token), token.dep_, token.head.text))
    return syntax


def print_mapping(sentence):
    """구문 분석 결과와 의미역 매핑을 함께 출력한다."""
    syntax = parse_syntax(sentence)
    print("문장:", sentence)

    if not syntax:
        print("- 의미 해석에 연결할 구문 관계를 찾지 못했습니다.")
        print()
        return

    # 1단계: 구문 분석 결과
    for chunk, dep, head in syntax:
        print(f"구성요소: {chunk:24} | 구문관계: {dep:5} | 중심어: {head}")

    # 2단계: 구문 관계 → 의미역 연결
    print("\n의미 해석 연결:")
    for chunk, dep, _ in syntax:
        print(f"- {chunk} → {semantic_map.get(dep, '기타')}")
    print()


if __name__ == "__main__":
    # 주어-목적어, 어순 변화, 여격, 장소 부가어 등 다양한 예문
    sentences = [
        "Der Student liest das Buch.",
        "Der Hund beißt den Mann.",
        "Den Mann beißt der Hund.",
        "Die Mutter gibt dem Kind ein Buch.",
        "Der Student liest das Buch in der Bibliothek.",
    ]

    for sentence in sentences:
        print_mapping(sentence)
