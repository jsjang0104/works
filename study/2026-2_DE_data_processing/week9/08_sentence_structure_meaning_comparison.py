"""08. 문장 구조와 의미 해석 비교

독일어에서 어순이 바뀌어도
격(Nominativ/Akkusativ) 정보 덕분에
행위자·대상 역할이 유지되는 예를 보여 줍니다.
→ '형태(어순)'와 '의미(역할)'가 항상 같지 않음을 확인합니다.
"""

# 어순은 다르지만 의미역은 같은 두 문장
sentences = [
    "Der Hund beißt den Mann.",   # 주어-동사-목적어 (기본 어순)
    "Den Mann beißt der Hund.",   # 목적어를 앞으로 보낸 어순
]

for s in sentences:
    print("문장:", s)
    # Nominativ(Der Hund) = 행위자, Akkusativ(den Mann) = 대상
    print("해석 핵심: Hund=행위자, Mann=대상")
    print()
