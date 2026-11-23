"""BLEU: 독일어 기계번역의 n-gram 정밀도 평가. pip install sacrebleu

BLEU는 가설(번역 결과)의 n-gram이 참조(정답 번역)에 얼마나 겹치는지를 봅니다.
점수가 높을수록 표면 형태가 참조와 가깝다는 뜻이며, 동의어 교체는 낮게 평가될 수 있습니다.
"""
import sacrebleu

# reference=정답 번역, hypothesis=모델이 만든 번역
reference = "Das Mädchen liest heute ein interessantes Buch."
hypothesis = "Das Mädchen liest heute ein spannendes Buch."  # interessant ↔ spannend: 의미는 가깝지만 어휘가 다름

# corpus_bleu는 (가설 리스트, 참조 리스트의 리스트)를 받습니다.
# 참조가 여러 개일 수 있어 [[reference]]처럼 한 겹 더 감쌉니다.
# 한 문장만 넣어도 코퍼스 함수를 쓰는 이유는, 실제 평가도 보통 문장 묶음 단위이기 때문입니다.
score = sacrebleu.corpus_bleu([hypothesis], [[reference]])
print(f"BLEU: {score.score:.2f}")  # 보통 0~100. 높을수록 좋음
# 이 예는 동의어만 바뀌었으므로, 의미가 비슷해도 BLEU는 낮게 나올 수 있습니다.
