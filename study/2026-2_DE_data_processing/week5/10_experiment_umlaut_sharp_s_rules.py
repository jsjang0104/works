# ==========================================================
# Umlaut, ß, 특수문자 유지 또는 변환 규칙 실험
#
# 독일어에는 ä, ö, ü, ß처럼 ASCII(영어 알파벳)에 없는 글자가 있습니다.
# 어떤 분석은 원형을 유지하고, 어떤 검색/정렬은 ae, oe, ue, ss로 바꿉니다.
# 두 결과를 나란히 보며 차이를 확인합니다.
#
# 기능:
# 1. 독일어 특수문자를 그대로 유지한 버전과 ASCII 대체 버전을 비교한다.
# 2. 교육 목적상 두 방식을 모두 관찰할 수 있게 구성한다.
#
# 용어 안내:
# - Umlaut: ä, ö, ü (모음 위의 점 두 개)
# - ß (Eszett, scharfes S): 영어 ss에 가까운 독일어 특수 문자
# - ASCII 대체: 특수문자를 영어 알파벳만으로 바꾸는 표기
# ==========================================================


sample_words = [
    "schön",
    "Mädchen",
    "König",
    "über",
    "Straße",
    "groß",
    "Maße"
]


def normalize_german_ascii(text):
    """움라우트와 ß를 전통적인 ASCII 대체 표기로 바꿉니다."""

    # 바꿀 글자(old) → 대체 문자열(new)
    replacements = {
        "ä": "ae", "ö": "oe", "ü": "ue",
        "Ä": "Ae", "Ö": "Oe", "Ü": "Ue",
        "ß": "ss"
    }

    # 사전을 하나씩 꺼내 해당 글자를 모두 바꿉니다.
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


print("=== 원형 유지 버전 ===")
for word in sample_words:
    print(word)

print("\n=== 대체 표기 버전 ===")
for word in sample_words:
    print(f"{word} -> {normalize_german_ascii(word)}")
