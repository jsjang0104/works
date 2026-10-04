# 05_형태_정보_관찰.py
# 독일어 형태소 분석 실습 5: 형태 정보 관찰
#
# 이 파일의 목적:
#   - 각 토큰의 morph(형태 자질)를 살펴본다.
#   - 예: 성(Gender), 수(Number), 격(Case), 시제(Tense) 등
#   - 독일어처럼 굴절이 풍부한 언어에서 특히 중요함

import spacy

nlp = spacy.load("de_core_news_sm")
text = "Die Kinder spielen im großen Garten."
doc = nlp(text)

print("문장:", text)
print("\n토큰별 형태 정보")

for token in doc:
    # token.morph: MorphAnalysis 객체 (자질이 없으면 빈 값)
    # str(...)로 "Case=Nom|Number=Plur" 같은 문자열로 변환
    morph = str(token.morph) if token.morph else "-"
    # {token.text:15}: 토큰을 15칸 너비로 맞춰 가독성 확보
    print(f"{token.text:15} -> {morph}")
