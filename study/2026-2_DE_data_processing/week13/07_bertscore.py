"""BERTScore: 문맥 임베딩 정렬 기반 의미 유사도. pip install bert-score torch

단어가 달라도 문맥 벡터가 비슷하면 높은 점수가 나옵니다.
n-gram 중복(BLEU/ROUGE)이 놓치는 의역·동의어를 더 잘 반영합니다.
"""
from bert_score import score

# reference = 정답(참조) 문장. 후보문과 의미가 얼마나 비슷한지 비교의 기준이 됩니다.
reference = "Die Universität bietet einen Kurs über künstliche Intelligenz an."

# candidates = 모델이 만든 후보 문장들
# A: KI ≈ künstliche Intelligenz (의역·약어 → 의미는 비슷, 표면형은 다름)
# B: keinen이 들어가 의미가 반대 → 점수가 낮아져야 정상입니다.
candidates = [
    "An der Universität wird ein Kurs über KI angeboten.",
    "Die Universität bietet keinen Kurs über künstliche Intelligenz an.",
]

# BERTScore 계산
# cands: 후보 문장 리스트 / refs: 참조 문장 리스트(후보마다 하나씩 대응)
# lang="de": 독일어용 사전학습 모델을 사용 (최초 실행 시 다운로드)
# idf=False: 희귀 단어 가중(IDF)을 쓰지 않음 → 수업용으로 해석이 단순해집니다.
# rescale_with_baseline=False: 원점수를 그대로 둠
# return_hash=True: 사용한 모델·설정 정보를 함께 반환해 재현성을 확인할 수 있습니다.
(scores, settings) = score(
    cands=candidates,
    refs=[reference, reference],
    lang="de",
    idf=False,
    rescale_with_baseline=False,
    return_hash=True,
)

# scores는 (Precision, Recall, F1) 텐서 튜플입니다.
# P: 후보 토큰이 참조와 얼마나 맞는지 / R: 참조 내용이 후보에 얼마나 남았는지
# F1: P와 R의 조화평균
precision, recall, f1 = scores

print("BERTScore 설정:", settings)

# 후보 A(의역)와 B(의미 반전)의 점수를 나란히 비교합니다.
for i, label in enumerate(("A", "B")):
    print(
        f"참조문–후보문 {label}: "
        f"P={precision[i].item():.6f}, "
        f"R={recall[i].item():.6f}, "
        f"F1={f1[i].item():.6f}"
    )
# 기대: A는 표면형이 달라도 의미가 가까워 상대적으로 높고,
#       B는 부정어로 의미가 바뀌어 상대적으로 낮게 나옵니다.
