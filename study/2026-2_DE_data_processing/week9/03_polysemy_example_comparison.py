"""03. 독일어 다의어 예문 비교

같은 단어(Bank)가 문맥에 따라
서로 다른 의미(금융기관 / 벤치)로 쓰이는 예를 보여 줍니다.
다의어(Polysemy) 개념을 직관적으로 이해하기 위한 도입 실습입니다.
"""

# 의미(한국어) → 해당 의미로 해석되는 독일어 예문
examples = {
    "금융기관": "Ich gehe zur Bank, um Geld abzuheben.",  # 돈을 찾으러 은행에
    "벤치": "Wir sitzen auf der Bank im Park.",            # 공원 벤치에 앉다
}

# 의미 라벨과 예문을 나란히 출력해 비교
for sense, sentence in examples.items():
    print(f"[{sense}] {sentence}")
