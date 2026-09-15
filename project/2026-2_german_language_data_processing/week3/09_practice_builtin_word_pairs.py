"""
enumerate(), zip(), sorted()로 독일어 단어 목록 정리하기

독일어 단어 리스트와 한국어 뜻 리스트가 따로 있을 때
같은 위치끼리 짝을 짓고, 번호를 붙이고, 길이순으로 정렬합니다.

이 예제에서 익히는 것:
    - zip()       : 두 리스트의 같은 칸끼리 짝 짓기
    - enumerate() : 번호와 값을 함께 꺼내기
    - list()      : zip 결과를 리스트로 저장하기
    - sorted()    : 새 순서로 정렬하기 (원본은 그대로)
    - key=        : 무엇을 기준으로 정렬할지 정하기
    - lambda      : 이름 없이 짧게 쓰는 함수
"""

# 같은 위치끼리 짝이 되는 독일어 단어와 한국어 뜻입니다.
# 1번째 칸: Haus ↔ 집,  2번째 칸: Freund ↔ 친구,  ...
german_words = ["Haus", "Freund", "Universität", "Buch", "Zeitung"]
korean_meanings = ["집", "친구", "대학교", "책", "신문"]


print("===== 원래 단어 목록 =====")

# zip(독일어, 한국어) : 같은 칸끼리 (독일어, 한국어) 쌍을 만듭니다.
#   예: ("Haus", "집"), ("Freund", "친구"), ...
#
# enumerate(..., start=1) : 그 쌍에 번호를 붙입니다.
#   start=1 을 주면 번호가 0이 아니라 1부터 시작합니다.
#   예: 1. ("Haus", "집"),  2. ("Freund", "친구"), ...
#
# for number, (german, korean) in ...
#   number : 번호 (1, 2, 3, ...)
#   german : 독일어 단어
#   korean : 한국어 뜻
#   (german, korean)처럼 괄호를 쓰는 이유:
#       enumerate가 주는 값이 (번호, (독일어, 한국어)) 형태이기 때문입니다.
for number, (german, korean) in enumerate(zip(german_words, korean_meanings), start=1):
    # f"...{변수}..." : 문장 안에 변수 값을 끼워 넣습니다.
    print(f"{number}. {german} : {korean}")


# zip()의 결과는 한 번만 꺼내 쓸 수 있는 특별한 묶음입니다.
# list()로 감싸면 나중에 여러 번 쓸 수 있는 리스트가 됩니다.
#   word_pairs 예: [("Haus", "집"), ("Freund", "친구"), ...]
word_pairs = list(zip(german_words, korean_meanings))

# sorted(리스트, key=...) : 원본은 그대로 두고, 새 순서로 정렬한 리스트를 만듭니다.
#
# key= 는 "무엇을 보고 순서를 정할까?"입니다.
#   기본 sorted()     → 알파벳(가나다) 순
#   key=... 를 주면  → 그 기준으로 작은 것부터 큰 것 순
#
# lambda pair: len(pair[0])
#   lambda : "이름 없는 짧은 함수"입니다. 한 줄짜리 계산에 자주 씁니다.
#   pair   : 한 쌍, 예: ("Haus", "집")
#   pair[0]: 쌍의 첫 번째 값 = 독일어 단어  ("Haus")
#   pair[1]: 쌍의 두 번째 값 = 한국어 뜻    ("집")
#   len(pair[0]) : 독일어 단어의 글자 수
#     Haus        → 4글자
#     Freund      → 6글자
#     Universität → 11글자
#     Buch        → 4글자
#     Zeitung     → 7글자
#
# 따라서 짧은 독일어 단어가 앞에 옵니다.
# (같은 길이끼리는 원래 순서를 유지하는 경우가 많습니다. Haus가 Buch보다 앞에 있음)
sorted_pairs = sorted(word_pairs, key=lambda pair: len(pair[0]))

print("\n===== 독일어 단어 길이순 목록 =====")
# sorted_pairs 안의 각 쌍을 다시 (독일어, 한국어)로 꺼내 출력합니다.
for german, korean in sorted_pairs:
    # len(german) : 그 독일어 단어가 몇 글자인지 셉니다.
    print(f"{german} ({len(german)}글자) : {korean}")
