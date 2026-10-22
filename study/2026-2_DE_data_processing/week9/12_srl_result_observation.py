"""12. SRL(Semantic Role Labeling) 결과 관찰

의미역 부착(SRL) 결과를 표(DataFrame)로 정리해 보는 예시입니다.
Predicate(서술어)와 Role(의미역), Phrase(표면 구)의
전형적인 표기 형식을 익힙니다.
"""

import pandas as pd

# 예시: "Der Arzt öffnet die Tür mit dem Schlüssel."
# ARG0 = 행위자, ARG1 = 대상, ARG2 = 도구(또는 간접 논항)
srl_result = pd.DataFrame([
    {"Predicate": "öffnen", "Role": "ARG0", "Phrase": "Der Arzt"},
    {"Predicate": "öffnen", "Role": "ARG1", "Phrase": "die Tür"},
    {"Predicate": "öffnen", "Role": "ARG2", "Phrase": "mit dem Schlüssel"},
])

print(srl_result)
