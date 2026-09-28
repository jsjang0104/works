# 실습 3: 관심 단어가 문장에 있는지 찾기
sentence = "Ich lerne Python und analysiere deutsche Texte."
keyword = input("찾을 단어를 입력하세요: ").lower()

sentence_lower = sentence.lower()

if keyword in sentence_lower:
    position = sentence_lower.find(keyword)
    print(f"'{keyword}'를 찾았습니다.")
    print("시작 위치:", position)
else:
    print(f"'{keyword}'를 찾지 못했습니다.")

print("분석한 문장:", sentence)
