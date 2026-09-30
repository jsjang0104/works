# ==========================================================
# 결과 비교 및 오류 사례 확인
#
# 같은 문장을 두 가지 방식으로 잘라 보면,
# 약어·따옴표·하이픈에서 결과가 달라집니다.
# "어떤 방법이 항상 정답"이 아니라, 목적에 따라 고른다는 점을 봅니다.
#
# 기능:
# 1. 공백 기반 분리와 정규표현식 기반 토큰화를 비교한다.
# 2. 약어, 따옴표, 하이픈 표현에서 어떤 차이가 나는지 관찰한다.
# 3. 토큰화 방식 선택이 분석 결과에 영향을 준다는 점을 이해한다.
# ==========================================================

import re


sample_texts = [
    "„Deutschland ist groß“, sagte er.",       # 따옴표·쉼표가 단어에 붙는 경우
    "Das ist z.B. ein wichtiges Thema.",       # 약어의 점이 문장부호처럼 보이는 경우
    "Die E-Mail-Adresse ist neu."              # 하이픈으로 이어진 복합어
]

# [A-Za-zÄÖÜäöüß]+              : 독일어 단어
# (?:-[A-Za-zÄÖÜäöüß]+)*        : 뒤에 -단어 가 0번 이상 반복 (E-Mail-Adresse를 하나로)
# |[.,!?„“\"():;]               : 또는 문장부호 1글자
pattern = r"[A-Za-zÄÖÜäöüß]+(?:-[A-Za-zÄÖÜäöüß]+)*|[.,!?„“\"():;]"

for idx, text in enumerate(sample_texts, start=1):
    print(f"\n=== 예문 {idx} ===")
    print(text)

    split_tokens = text.split()              # 방법 1: 공백만으로 자르기
    regex_tokens = re.findall(pattern, text) # 방법 2: 패턴으로 단어/기호 찾기

    print("- 공백 기반 분리:")
    print(split_tokens)

    print("- 정규표현식 기반 분리:")
    print(regex_tokens)

print("\n=== 관찰 포인트 ===")
print("1. 공백 기반 분리는 문장부호가 단어에 붙어 남는다.")
print("2. 약어(z. B.)는 단순 분리에서 부정확하게 처리될 수 있다.")
print("3. 하이픈 표현(E-Mail-Adresse)은 규칙에 따라 하나 또는 여러 토큰으로 처리될 수 있다.")
