# 실습 2: 독일어 문장 정리하기
sentence = "  Die Sprache, ist sehr WICHTIG!  "

cleaned = sentence.strip()                 # 앞뒤 공백 제거
cleaned = cleaned.lower()                   # 소문자 변환
cleaned = cleaned.replace(",", "")         # 쉼표 제거
cleaned = cleaned.replace("!", "")         # 느낌표 제거
word_list = cleaned.split()

print("정리 전:", sentence)
print("정리 후:", cleaned)
print("단어 목록:", word_list)
print("단어 수:", len(word_list))
