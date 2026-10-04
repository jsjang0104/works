# 13_분석결과_통합.py
# 독일어 통합 분석 실습 13: 형태소 분석·품사 태깅·표제어 추출 결과 통합
#
# 이 파일의 목적:
#   - 토큰마다 여러 분석 결과를 한 행으로 모아 표(DataFrame)로 본다.
#   - 수업·보고서에서 "한눈에 비교"하기 좋은 형태

import spacy
import pandas as pd

nlp = spacy.load("de_core_news_sm")
text = "Die Forscherinnen untersuchten sprachliche Daten, entwickelten neue Modelle und erklärten ihre Ergebnisse sehr präzise."
doc = nlp(text)

# 각 토큰의 정보를 딕셔너리로 쌓아 두면 DataFrame으로 바로 변환 가능
rows = []
for token in doc:
    rows.append({
        "token": token.text,           # 표층형
        "lemma": token.lemma_,         # 표제어
        "pos": token.pos_,             # 범용 품사
        "tag": token.tag_,             # 세부 품사 태그
        "morph": str(token.morph) if token.morph else "-",  # 형태 자질
        "dependency": token.dep_       # 의존 구문 관계 라벨 (nsubj, dobj 등)
    })

df = pd.DataFrame(rows)
print("통합 분석 결과표")
# to_string(index=False): 행 번호 없이 표 전체를 문자열로 출력
print(df.to_string(index=False))
