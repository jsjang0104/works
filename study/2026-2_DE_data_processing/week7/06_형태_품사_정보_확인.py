# 각 토큰의 형태·품사 정보를 확인합니다.
# 구조 분석 전에 형태론적 정보를 파악하는 단계입니다.

import spacy

nlp = spacy.load("de_core_news_sm")
doc = nlp("Der kluge Student liest heute in der Bibliothek ein altes Buch.")

for token in doc:
    print({
        "token": token.text,    # 표면형(문장에 나타난 형태)
        "lemma": token.lemma_,  # 기본형(원형)
        "pos": token.pos_,      # 보편 품사 태그 (NOUN, VERB, ADP 등)
        "tag": token.tag_,      # 언어별 세분 품사 태그 (독일어 STTS)
        "morph": token.morph    # 형태 자질 (격, 수, 성, 시제 등)
    })
