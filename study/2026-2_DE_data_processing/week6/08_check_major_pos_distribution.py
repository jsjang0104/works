# 08_주요_품사_범주의_분포_점검.py
# 독일어 품사 태깅 실습 8: 주요 품사 범주의 분포 점검
#
# 이 파일의 목적:
#   - 문장(또는 텍스트)에서 품사별 출현 횟수를 센다.
#   - 말뭉치 통계, 텍스트 특성 파악의 기본 단계

import spacy
from collections import Counter  # 항목별 개수를 세는 딕셔너리형 도구

nlp = spacy.load("de_core_news_sm")
text = "Der alte Professor erklärt den Studierenden die linguistischen Modelle, während sie aufmerksam zuhören und Notizen schreiben."
doc = nlp(text)

# 제너레이터 식으로 모든 토큰의 pos_를 모아 한꺼번에 집계
pos_counts = Counter(token.pos_ for token in doc)

print("문장:", text)
print("\n품사 분포")
for pos, count in pos_counts.items():
    print(f"{pos:10} : {count}")
