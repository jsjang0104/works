# 구구조/의존구조에서 핵심이 되는 '중심어(head)' 후보를 미리 예측합니다.
# 명사구의 중심은 보통 명사, 전치사구의 중심은 전치사, 문장의 중심은 본동사입니다.

sentence = "Der erfahrene Linguist analysiert die komplexe Satzstruktur mit großer Sorgfalt."

head_candidates = {
    "명사구 후보 1": "Linguist",          # Der erfahrene Linguist의 중심어
    "명사구 후보 2": "Satzstruktur",      # die komplexe Satzstruktur의 중심어
    "전치사구 후보": "mit",               # mit großer Sorgfalt의 중심어
    "문장 중심 동사 후보": "analysiert"   # 문장 전체의 ROOT 후보
}

for k, v in head_candidates.items():
    print(f"{k}: {v}")
