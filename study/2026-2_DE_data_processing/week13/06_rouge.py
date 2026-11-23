"""ROUGE: 독일어 요약문의 단어 중복 기반 재현율 평가. pip install rouge-score

BLEU가 '정밀도(가설이 참조에 얼마나 포함되나)'에 가깝다면,
ROUGE는 '재현율(참조의 내용이 가설에 얼마나 남았나)'을 함께 봅니다. 요약 평가에 자주 씁니다.
"""
from rouge_score import rouge_scorer

# reference=정답 요약, hypothesis=모델이 만든 요약(또는 압축된 문장)
reference = "Die Bundesregierung beschloss neue Maßnahmen zum Klimaschutz."
hypothesis = "Die Regierung hat neue Klimaschutzmaßnahmen beschlossen."

# rouge1=단어(1-gram), rouge2=연속 두 단어, rougeL=최장공통부분수열(어순을 어느 정도 반영)
# use_stemmer=False: 독일어 어간 추출이 영어 중심이라 이 실습에서는 표면형을 그대로 비교합니다.
scorer = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=False)
# score()는 각 지표마다 precision(P), recall(R), fmeasure(F1)를 돌려줍니다.
for name, result in scorer.score(reference, hypothesis).items():
    print(f"{name}: P={result.precision:.3f}, R={result.recall:.3f}, F1={result.fmeasure:.3f}")
# 복합어(Klimaschutzmaßnahmen)처럼 띄어쓰기가 다르면 단어 단위 점수가 낮아질 수 있습니다.
