# 14_오류_또는_한계_사례_검토.py
# 독일어 통합 분석 실습 14: 오류 또는 한계 사례 검토
#
# 이 파일의 목적:
#   - 자동 분석이 항상 완벽하지 않음을 경험한다.
#   - 긴 복합어·신조어·전문용어에서 자주 나타나는 한계를 검토한다.

import spacy

nlp = spacy.load("de_core_news_sm")
# 매우 긴 복합어 + 다소 특수한 어휘 → 모델이 어려워할 수 있는 문장
text = "Donaudampfschifffahrtsgesellschaftskapitän erklärt neue Forschungswörter präzise."
doc = nlp(text)

print("문장:", text)
print("\n분석 결과")
for token in doc:
    print(
        f"{token.text:40} | "
        f"POS={token.pos_:6} | "
        f"lemma={token.lemma_:20} | "
        f"morph={str(token.morph) if token.morph else '-'}"
    )

# 결과를 보며 아래 관점으로 토론·검토해 보세요
print("\n오류 또는 한계 검토")
print("- 복합어 내부 구조는 자동으로 세분화되지 않을 수 있다.")
print("- 신조어와 전문용어는 품사 태깅이 부정확할 수 있다.")
print("- 표제어 추출은 문맥과 학습 데이터의 한계에 영향을 받는다.")
