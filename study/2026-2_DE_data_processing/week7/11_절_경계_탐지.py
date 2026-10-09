# 종속절(dass-절)이 있는 문장에서 절 경계를 관찰합니다.
# 독일어 종속절은 활용 동사가 절 말미에 오는 것이 특징입니다.

import spacy

nlp = spacy.load("de_core_news_sm")
doc = nlp("Die Studentin sagt, dass der Professor heute keine Vorlesung hält.")

# 각 토큰의 위치, 표면형, 품사, 의존라벨, 중심어를 함께 출력
for token in doc:
    print(token.i, token.text, token.pos_, token.dep_, token.head.text)

print("\n절 경계 탐지 포인트:")
print("- 쉼표 이후 'dass'가 종속절을 시작하는지 확인")
print("- 종속절의 활용 동사 'hält'가 절 말미에 오는지 확인")
