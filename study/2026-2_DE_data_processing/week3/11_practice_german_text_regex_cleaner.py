# 정규 표현식으로 독일어 텍스트 정리 및 단어 추출하기
import re

text = "  Die   Universität München bietet E-Mail-Kurse an!  \nDeutsch, Deutsch; und KI: spannend.  "

# \s+는 공백, 탭, 줄바꿈이 1개 이상 이어진 부분을 뜻합니다.
# 이를 공백 하나로 바꾸어 텍스트를 정리합니다.
clean_text = re.sub(r"\s+", " ", text).strip()

# 독일어 알파벳 äöüÄÖÜß와 하이픈(-)을 포함한 단어를 찾습니다.
# 예: E-Mail도 한 단어로 추출됩니다.
words = re.findall(r"[A-Za-zÄÖÜäöüß]+(?:-[A-Za-zÄÖÜäöüß]+)*", clean_text)

# 대소문자를 구분하지 않고 'deutsch'가 몇 번 나오는지 확인합니다.
deutsch_count = len(re.findall(r"\bDeutsch\b", clean_text, flags=re.IGNORECASE))

print("===== 정리된 텍스트 =====")
print(clean_text)
print("\n===== 추출한 단어 =====")
print(words)
print(f"\n'Deutsch'의 출현 횟수: {deutsch_count}")
