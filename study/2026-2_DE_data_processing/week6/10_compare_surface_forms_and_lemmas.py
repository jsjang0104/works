# 10_표층형과_표제어_비교.py
# 독일어 표제어 추출 실습 10: 표층형과 표제어 비교
#
# 이 파일의 목적:
#   - 표층형(token.text): 문장에 실제로 나타난 형태
#   - 표제어(token.lemma_): 사전 기본형 (lemmatization 결과)
#   - 굴절이 많은 독일어에서 "같은 단어"를 묶을 때 핵심 전처리

import spacy

nlp = spacy.load("de_core_news_sm")
# gingen→gehen, Bibliotheken→Bibliothek, lasen→lesen, waren→sein 등을 기대해 볼 수 있음
text = "Die Kinder gingen in die Bibliotheken, lasen Bücher und waren sehr glücklich."
doc = nlp(text)

print("문장:", text)
print("\n표층형과 표제어 비교")
for token in doc:
    print(f"{token.text:18} -> {token.lemma_}")
