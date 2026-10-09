# 자동 분석 전에, 사람이 먼저 구(phrase) 경계를 예측해 보는 연습입니다.
# 괄호로 묶은 구간이 하나의 통사 성분인지 생각해 보세요.

sentence = "Die junge Studentin aus München liest in der alten Bibliothek ein sehr spannendes Buch."

print("문장:", sentence)
print("예측 질문")
print("1) [Die junge Studentin]은 하나의 명사구인가?")           # NP: 관사+형용사+명사
print("2) [aus München]은 전치사구인가?")                        # PP: 전치사+명사
print("3) [in der alten Bibliothek]은 부사어 역할을 하는가?")    # 장소 부사어(PP)
print("4) [ein sehr spannendes Buch]은 목적어 명사구인가?")      # 목적어 NP
