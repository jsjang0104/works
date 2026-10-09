# 구조적으로 모호한 문장 쌍을 비교합니다.
# 전치사구 'mit ...'가 동사에 붙는지(도구/수단), 명사에 붙는지(수식)에 따라
# 의미가 달라질 수 있습니다. (classic PP attachment ambiguity)

examples = [
    "Ich sehe den Mann mit dem Fernglas.",  # mit dem Fernglas: 망원경으로 보다? / 망원경을 든 남자?
    "Ich sehe den Mann mit dem Hut."        # mit dem Hut: 보통 '모자를 쓴 남자'로 해석
]

print("구조적 모호성 토론 예시")
for sent in examples:
    print("-", sent)
    print("  → 'mit ...'가 'sehen'에 붙는가, 'den Mann'에 붙는가?")
