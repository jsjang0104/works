# 의존구문분석에서 각 토큰의 중심어(head)를 확인합니다.
# head는 "이 단어가 문법적으로 무엇을 수식/의존하는가"를 나타냅니다.

import spacy

nlp = spacy.load("de_core_news_sm")
doc = nlp("Der Student liest das Buch aufmerksam.")

for token in doc:
    # token.head: 이 토큰이 의존하는 상위 토큰(중심어)
    print(f"token={token.text:12} head={token.head.text:12}")
