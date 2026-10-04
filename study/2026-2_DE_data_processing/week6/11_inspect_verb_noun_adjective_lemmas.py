# 11_동사_명사_형용사의_표제어_확인.py
# 독일어 표제어 추출 실습 11: 동사·명사·형용사의 표제어 확인
#
# 이 파일의 목적:
#   - 기능어(관사·전치사 등)를 건너뛰고 내용어(VERB/NOUN/ADJ)만 본다.
#   - 어휘 목록·의미 분석에서는 내용어 표제어가 더 유용한 경우가 많음

import spacy

nlp = spacy.load("de_core_news_sm")
text = "Die Kinder gingen in die Bibliotheken, lasen Bücher und waren sehr glücklich."
doc = nlp(text)

print("내용어 중심 표제어 확인")
for token in doc:
    # Universal POS 기준으로 동사·명사·형용사만 필터
    if token.pos_ in {"VERB", "NOUN", "ADJ"}:
        print(f"{token.text:18} | POS={token.pos_:5} | lemma={token.lemma_}")
