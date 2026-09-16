# 실습 1: 독일어 문장 기본 정보 확인하기
sentence = "Ich studiere Germanistik in Korea."

character_count = len(sentence)
word_list = sentence.split()
word_count = len(word_list)

print("원문:", sentence)
print("문자 수(공백 포함):", character_count)
print("단어 목록:", word_list)
print("단어 수:", word_count)
