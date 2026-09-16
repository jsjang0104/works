"""
텍스트 통계 구하기

독일어(또는 영어) 글을 넣으면
문자 수, 단어 수, 문장 수, 자주 나온 단어를 알려 줍니다.

이 예제에서 익히는 것:
    - import : 미리 만들어 둔 도구(모듈)를 불러오기
    - 함수(def) : 같은 일을 이름 붙여 다시 쓰기
    - len() : 글자나 항목이 몇 개인지 세기
    - 정규표현식(re) : 글 속에서 원하는 패턴만 찾기
    - set() : 중복을 없애고 고유한 값만 남기기
    - Counter : 각 값이 몇 번 나왔는지 세어 주기
"""

# collections 모듈에서 Counter만 가져옵니다.
# Counter는 "이 값이 몇 번 나왔나?"를 세어 주는 도구입니다.
# 예: Counter(["python", "python", "ki"]) → python 2번, ki 1번
from collections import Counter

# re 모듈 = 정규표현식(regular expression) 도구 상자
# "글 속에서 이런 모양의 부분만 찾아 줘"라고 패턴으로 말할 때 씁니다.
import re


def text_statistics(text):
    """글 하나를 받아서 문자/단어/문장 통계를 출력합니다."""

    # len()은 길이를 셉니다.
    # 문자열이면 글자 수(공백, 물음표 포함)입니다.
    char_count = len(text)

    # replace(" ", "") : 공백(" ")을 빈 문자열("")로 바꿉니다.
    # 즉, 띄어쓰기를 모두 지운 뒤 글자 수를 셉니다.
    char_no_space = len(text.replace(" ", ""))

    # re.findall(패턴, 글) : 패턴에 맞는 부분을 모두 찾아 리스트로 줍니다.
    #
    # text.lower() : 대문자를 소문자로 바꿉니다.
    #   Python / PYTHON / python 을 같은 단어로 세기 위해서입니다.
    #
    # r"\b\w+\b" 패턴 설명:
    #   \b  : 단어의 경계 (단어가 시작하거나 끝나는 자리)
    #   \w  : 글자(알파벳, 숫자, 밑줄). 독일어 ä, ö, ü, ß 도 포함됩니다.
    #   +   : 바로 앞 것이 1개 이상
    #   즉 "단어처럼 생긴 덩어리"를 모두 찾습니다.
    words = re.findall(r"\b\w+\b", text.lower())

    # 찾은 단어 리스트의 길이 = 전체 단어 수
    word_count = len(words)

    # set()은 집합입니다. 같은 값은 하나만 남깁니다.
    # 예: ["python", "python", "ki"] → {"python", "ki"}
    # 그래서 고유 단어(서로 다른 단어) 개수를 알 수 있습니다.
    unique_word_count = len(set(words))

    # re.split(패턴, 글) : 패턴이 나온 자리에서 글을 잘라 리스트로 만듭니다.
    # r"[.!?]+" : 마침표(.), 느낌표(!), 물음표(?)가 1개 이상 이어진 곳
    #
    # 리스트 컴프리헨션:
    #   [s for s in ... if 조건]
    #   잘라 낸 조각 s 중에서, 공백만 있는 조각은 빼고 진짜 문장만 남깁니다.
    #   s.strip() : 앞뒤 공백을 지웁니다. 남은 글이 있으면 True 입니다.
    sentences = [s for s in re.split(r"[.!?]+", text) if s.strip()]
    sentence_count = len(sentences)

    # Counter(words) : 각 단어가 몇 번 나왔는지 세어 딕셔너리처럼 저장합니다.
    word_freq = Counter(words)

    print("===== 텍스트 통계 =====")
    print("문자 수(공백 포함):", char_count)
    print("문자 수(공백 제외):", char_no_space)
    print("단어 수:", word_count)
    print("고유 단어 수:", unique_word_count)
    print("문장 수:", sentence_count)

    print("\n===== 상위 단어 =====")
    # most_common(10) : 가장 많이 나온 단어 10개를 (단어, 횟수)로 줍니다.
    # for word, count in ... : 한 줄씩 단어와 횟수를 꺼내 출력합니다.
    for word, count in word_freq.most_common(10):
        print(f"{word}: {count}")


# 통계를 내 볼 샘플 글입니다. (독일어 문장)
sample_text = "Was ist Ihrer Meinung nach die beliebteste Programmiersprache für Datenanalyse, künstliche Intelligenz und Webentwicklung? Python! Besonders im Bereich der natürlichen Sprachverarbeitung wird Python sehr häufig eingesetzt! Deshalb sollte man Python unbedingt lernen, wenn man KI studieren oder entwickeln möchte."

# 위에서 만든 함수에 샘플 글을 넣어 실행합니다.
text_statistics(sample_text)
