# 실습 4: 독일어 단어 빈도 세기
text = "Die Sprache ist wichtig. Die Sprache verbindet Menschen."

# 초보 단계에서는 분석 대상의 문장부호를 직접 제거한다.
cleaned = text.lower().replace(".", "")
words = cleaned.split()
frequency = {}

for word in words:
    if word in frequency:
        frequency[word] = frequency[word] + 1
    else:
        frequency[word] = 1

print("단어별 빈도")
for word, count in frequency.items():
    print(word, ":", count)

most_frequent_word = ""
most_frequent_count = 0
for word, count in frequency.items():
    if count > most_frequent_count:
        most_frequent_word = word
        most_frequent_count = count

print("가장 자주 나온 단어:", most_frequent_word)
print("최대 빈도:", most_frequent_count)
