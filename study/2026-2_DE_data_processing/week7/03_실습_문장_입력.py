# 이후 실습에서 사용할 독일어 예문 목록을 준비합니다.
# 문장 구조가 점차 복잡해지도록 구성했습니다.

sentences = [
    # 1) 단순 주어-동사-목적어 + 장소 부사구
    "Der Student liest das interessante Buch in der Bibliothek.",
    # 2) 관계절이 포함된 문장 (삽입된 종속절)
    "Die Professorin, die gestern aus Berlin gekommen ist, erklärt die Syntax sehr genau.",
    # 3) 원인 종속절(Weil ...) + 주절 구조
    "Weil der Forscher die Daten sorgfältig analysiert hat, konnte er ein klares Ergebnis präsentieren."
]

# 번호를 붙여 예문을 출력
for i, sent in enumerate(sentences, start=1):
    print(f"[{i}] {sent}")
