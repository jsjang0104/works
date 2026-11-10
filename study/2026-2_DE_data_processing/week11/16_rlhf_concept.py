"""16. RLHF: 선호 데이터로 보상 신호를 구성하는 개념 실습

이 파일은 실제 RLHF를 학습시키는 코드가 아닙니다.
"인간이 어떤 답을 더 좋아하는지"를 숫자 보상으로 바꾸는 아이디어만 보여 줍니다.

RLHF (Reinforcement Learning from Human Feedback):
- 사람의 선호(feedback)를 보상(reward)으로 바꿔,
  모델이 그 보상을 높이도록 정책을 조정하는 방법입니다.

실제 RLHF의 세 단계 (여기서는 1단계의 데이터 형태만 흉내 냄):
1) 인간 비교평가: 같은 질문에 대한 답 A, B 중 더 나은 쪽을 사람이 고른다
2) 보상모델(Reward Model): 그 비교를 예측하도록 학습한다
   → "이 답은 사람이 얼마나 좋아할까?"를 점수로 출력
3) 정책 최적화: PPO, DPO 등으로 높은 보상을 받는 답을 더 자주 내게 한다
   - PPO: 보상모델 점수를 강화 학습 보상으로 씀
   - DPO: 보상모델을 따로 두지 않고, 선호 쌍으로 정책을 직접 학습
"""


# ------------------------------------------------------------
# 기본 설정값 (수업/실습용)
# ------------------------------------------------------------
# 선호 쌍(preference pair) 데이터
#   각 튜플: (답 A, 답 B, 사람이 고른 쪽)
#   실제로는 같은 질문에 모델이 만든 서로 다른 두 답을 사람이 비교합니다.
#   여기서는 문장 내용은 예시이고, 핵심은 세 번째 값(선호 라벨)입니다.
DEFAULT_PAIRS = [
    ("Antwort A", "Antwort B", "A"),  # 사람이 A를 더 좋다고 평가
    ("Antwort A", "Antwort B", "B"),  # 사람이 B를 더 좋다고 평가
    ("Antwort A", "Antwort B", "A"),  # 사람이 다시 A를 선택
]


def validate_pairs(pairs):
    """선호 쌍 데이터 형식을 검사합니다."""
    if not pairs:
        raise ValueError("선호 쌍 데이터가 비어 있습니다.")
    for i, item in enumerate(pairs):
        if not isinstance(item, (tuple, list)) or len(item) != 3:
            raise ValueError(f"{i}번째 항목은 (답A, 답B, 선호라벨) 형식이어야 합니다.")
        _, _, preferred = item
        if preferred not in ("A", "B"):
            raise ValueError(f"{i}번째 선호 라벨은 'A' 또는 'B'여야 합니다. (받은 값: {preferred})")


def count_preferences(pairs):
    """각 답이 몇 번 선호되었는지 셉니다.

    실제 보상모델은 이런 단순 집계가 아니라,
    답의 내용을 보고 "선호될 확률/점수"를 예측하도록 학습합니다.
    """
    validate_pairs(pairs)
    score = {"A": 0, "B": 0}
    # _: 쓰지 않는 값(답 A, 답 B)을 버리겠다는 관례
    for _, _, preferred in pairs:
        score[preferred] += 1
    return score


def preference_rates(score):
    """선택 횟수를 비율(0~1)로 바꿉니다."""
    total = sum(score.values())
    if total == 0:
        return {"A": 0.0, "B": 0.0}
    return {k: v / total for k, v in score.items()}


def choose_winner(score):
    """더 많이 선호된 쪽을 반환합니다. 동점이면 None."""
    if score["A"] > score["B"]:
        return "A"
    if score["B"] > score["A"]:
        return "B"
    return None


def print_rlhf_report(pairs, score):
    """선호 집계 결과를 초보자가 읽기 쉽게 출력합니다."""
    rates = preference_rates(score)
    winner = choose_winner(score)

    print(f"선호 쌍 개수: {len(pairs)}")
    print("human preference counts:", score)
    print(
        "preference rates:",
        {k: round(v, 3) for k, v in rates.items()},
    )
    if winner is None:
        print("현재까지는 A와 B가 동점입니다.")
    else:
        print(f"상대적으로 더 선호된 쪽: {winner}")

    print()
    print("이 숫자가 곧 '보상 신호'의 씨앗입니다.")
    print("  - 보상모델은 이 비교 선호를 예측하도록 학습하고,")
    print("  - 정책(언어 모델)은 높은 보상을 받도록 조정됩니다.")
    print()
    print("관찰 포인트:")
    print("  - 핵심은 답의 문장 내용이 아니라 '어느 쪽이 선택되었는가'입니다.")
    print("  - 실제 RLHF는 이 선호 데이터로 보상모델/정책을 학습합니다.")
    print("  - 이 파일은 그 첫 단계(선호 집계)만 개념적으로 보여 줍니다.")


def run_rlhf_demo(pairs=None):
    """선호 쌍을 집계하고 결과를 출력합니다.

    이 함수만 호출해도 전체 실습 흐름이 실행됩니다.
    """
    if pairs is None:
        pairs = list(DEFAULT_PAIRS)
    score = count_preferences(pairs)
    print_rlhf_report(pairs, score)
    return score


def read_preference_pairs():
    """사용자에게 선호 라벨을 여러 줄로 입력받습니다.

    사용법:
    - 각 줄에 A 또는 B만 입력 (그 비교에서 이긴 쪽)
    - 빈 줄이면 종료
    - 아무 것도 없으면 기본 예제 사용
    """
    print("각 비교에서 선호한 쪽을 A 또는 B로 입력하세요.")
    print("(빈 줄을 누르면 입력 종료 / 아무 것도 안 쓰면 기본 예제 사용)")
    labels = []
    while True:
        line = input("> ").strip().upper()
        if not line:
            break
        if line not in ("A", "B"):
            print("  A 또는 B만 입력하세요.")
            continue
        labels.append(line)

    if not labels:
        return list(DEFAULT_PAIRS)

    # 입력은 라벨만 받으므로, 내용은 자리표시자로 채웁니다.
    return [("Antwort A", "Antwort B", label) for label in labels]


if __name__ == "__main__":
    # --------------------------------------------------
    # A. 기본 데모: 미리 준비한 선호 쌍 3개
    # --------------------------------------------------
    print("=" * 60)
    print("A. 기본 데모 (선호 집계 → 보상 신호 개념)")
    print("=" * 60)
    run_rlhf_demo()
    print()

    # --------------------------------------------------
    # B. 일반화: 사용자가 입력한 선호 라벨로 같은 절차 반복
    # --------------------------------------------------
    print("=" * 60)
    print("B. 직접 입력한 선호로 집계하기")
    print("=" * 60)
    user_pairs = read_preference_pairs()
    print()
    run_rlhf_demo(pairs=user_pairs)
