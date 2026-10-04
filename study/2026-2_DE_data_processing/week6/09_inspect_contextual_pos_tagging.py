# 09_문맥에_따른_품사_판정_사례_확인.py
# 독일어 품사 태깅 실습 9: 문맥에 따른 품사 판정 사례 확인
#
# 이 파일의 목적:
#   - 같은 형태라도 문맥에 따라 품사가 달라질 수 있음을 확인한다.
#   - 관심 단어만 골라 POS/TAG와 소속 문장을 출력한다.

import spacy

nlp = spacy.load("de_core_news_sm")
text = "Der alte Professor erklärt den Studierenden die linguistischen Modelle, während sie aufmerksam zuhören und Notizen schreiben."
doc = nlp(text)

# 관찰하고 싶은 단어들 (소문자 비교용 집합)
# 예: alte(형용사), aufmerksam(부사/형용사 가능), schreiben(동사) 등
targets = {"alte", "aufmerksam", "zuhören", "schreiben", "erklärt"}

print("문맥 기반 품사 판정 사례")
for token in doc:
    # 대소문자 차이를 무시하고 관심 단어인지 확인
    if token.text.lower() in targets:
        print(f"단어: {token.text}")
        print(f"- POS: {token.pos_}")
        print(f"- TAG: {token.tag_}")
        # token.sent: 이 토큰이 속한 문장(Span) — 문맥 확인용
        print(f"- 문맥: {token.sent.text}")
        print()
