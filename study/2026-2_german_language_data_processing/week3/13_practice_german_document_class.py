# 실습 5: 클래스와 표준 모듈로 독일어 문서 분석기 만들기
#
# 클래스(class)는 "같은 종류의 데이터를 다루는 설계도"입니다.
# 객체(object)는 그 설계도로 실제로 만든 한 권의 문서입니다.
#
# 비유:
#     클래스 GermanDocument = "독일어 문서 분석기" 설계도
#     객체 document         = 그 설계도로 만든 실제 문서 한 편
#     속성(title, text)     = 그 문서에 적힌 제목과 본문
#     메서드(함수)           = 그 문서를 세거나, 분석하거나, 출력하는 일

import re  # 정규표현식으로 본문에서 단어를 골라 냅니다.
from collections import Counter  # 단어가 몇 번 나왔는지 세는 표준 도구입니다.


class GermanDocument:
    """독일어 문서의 제목과 본문을 함께 관리하고 간단히 분석하는 클래스입니다."""

    def __init__(self, title, text):
        # __init__은 객체를 만들 때 자동으로 한 번 실행되는 준비 함수입니다.
        # self는 "지금 만들고 있는 이 객체 자신"을 가리킵니다.
        # self.속성은 객체마다 따로 저장되는 데이터입니다.
        self.title = title  # 문서 제목
        self.text = text    # 문서 본문

    def get_words(self):
        """본문에서 독일어 단어를 소문자 목록으로 반환합니다."""
        # lower()는 대소문자를 모두 소문자로 바꿉니다.
        # 예: Deutsch → deutsch  (같은 단어로 세기 위해)
        #
        # findall()은 패턴에 맞는 글자들을 모두 찾아 목록으로 돌려줍니다.
        # [A-Za-zÄÖÜäöüß]+  → 영어 알파벳과 독일어 특수문자(ä, ö, ü, ß)가
        #                     하나 이상 이어진 덩어리(= 단어)만 찾습니다.
        return re.findall(r"[A-Za-zÄÖÜäöüß]+", self.text.lower())

    def word_count(self):
        """전체 단어 수를 반환합니다."""
        # len()은 목록에 들어 있는 항목 개수입니다.
        # get_words()가 만든 단어 목록의 길이가 곧 전체 단어 수입니다.
        return len(self.get_words())

    def top_words(self, n=5):
        """가장 자주 나온 단어 n개를 (단어, 빈도) 형태로 반환합니다."""
        # n=5는 기본값입니다. 숫자를 안 주면 상위 5개를 보여 줍니다.
        #
        # Counter는 목록을 받아 "무엇이 몇 번?"을 세어 줍니다.
        # 예: ["deutsch", "ist", "deutsch"] → {"deutsch": 2, "ist": 1}
        frequencies = Counter(self.get_words())
        # most_common(n)은 가장 많이 나온 것부터 n개를 골라 줍니다.
        # 결과는 [("deutsch", 2), ("ist", 1), ...]처럼 (단어, 횟수) 쌍입니다.
        return frequencies.most_common(n)

    def print_report(self):
        """분석 결과를 화면에 보기 좋게 출력합니다."""
        # f-문자열: 중괄호 {} 안에 변수나 메서드 결과를 넣어 문장을 만듭니다.
        print(f"===== 문서 분석: {self.title} =====")
        print(f"전체 단어 수: {self.word_count()}")
        print("상위 빈도 단어:")
        # top_words()가 돌려준 (단어, 횟수) 쌍을 하나씩 꺼내 출력합니다.
        for word, count in self.top_words():
            print(f"- {word}: {count}회")


# GermanDocument(...)를 호출하면 __init__이 실행되고, 객체 하나가 만들어집니다.
# 첫 번째 인자는 제목, 두 번째 인자는 본문입니다.
document = GermanDocument(
    "독일어와 데이터",
    "Deutsch ist eine wichtige Sprache. Deutsch wird in vielen Ländern gesprochen. "
    "Daten und Sprache können mit Python analysiert werden."
)

# 점(.)은 "이 객체의 메서드를 실행하라"는 뜻입니다.
# document.print_report() → 위에서 만든 문서의 분석 결과를 출력합니다.
document.print_report()
