"""19. 의미는 유사하나 표현은 다른 문장 비교

패러프레이즈(paraphrase)의 개념 도입입니다.
단어·어순은 달라도 핵심 사건 의미가 비슷한 문장 쌍을 관찰합니다.
"""

# 표현은 다르지만 사건이 비슷한 문장 쌍
pairs = [
    # ankommen ≈ Bahnhof erreichen + pünktlich ≈ rechtzeitig
    ("Der Zug kommt pünktlich an.", "Der Zug erreicht rechtzeitig den Bahnhof."),
    # beginnen ≈ starten, 어순만 바뀐 경우
    ("Die Vorlesung beginnt um neun Uhr.", "Um neun Uhr startet die Vorlesung."),
]

for s1, s2 in pairs:
    print("문장 A:", s1)
    print("문장 B:", s2)
    print("해석: 표현은 다르지만 사건 의미는 유사함")
    print()
