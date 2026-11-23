"""LLM-as-a-Judge: 명시적 루브릭으로 독일어 생성문을 채점. pip install openai; OPENAI_API_KEY 설정 필요

자동 지표가 놓치는 문법·완전성·의미 적합성은 다른 언어모델에게 채점시킬 수 있습니다.
점수의 재현성을 높이려면 루브릭을 고정하고 temperature를 0으로 둡니다.
"""
from openai import OpenAI

client = OpenAI()  # 환경변수 OPENAI_API_KEY를 사용합니다.

# reference=채점 기준이 되는 정답 문장, candidate=평가할 생성문
reference = "Die Analyse deutscher Texte erfolgt reproduzierbar mit Python."
candidate = "Python ermöglicht eine nachvollziehbare Analyse deutscher Texte."

# 채점 기준(의미·문법·완전성)과 출력 형식(JSON)을 프롬프트에 고정합니다.
# JSON만 달라고 하면 이후 점수만 파싱하기 쉽습니다.
prompt = f'''Du bist ein strenger Bewertungsassistent. Bewerte die Kandidatenantwort
gegen die Referenz auf semantische Korrektheit, deutsche Grammatik und Vollständigkeit.
Referenz: {reference}
Kandidat: {candidate}
Gib NUR JSON aus: {{"score": 1-5, "begruendung": "..."}}.'''

# temperature=0: 같은 입력이면 가능한 한 같은 채점이 나오도록 무작위를 줄입니다.
response = client.chat.completions.create(model="gpt-4.1-mini", messages=[{"role":"user","content":prompt}], temperature=0)
print(response.choices[0].message.content)
# score는 1~5, begruendung은 독일어 근거입니다. 수업에서는 왜 그 점수인지 근거를 함께 읽습니다.
