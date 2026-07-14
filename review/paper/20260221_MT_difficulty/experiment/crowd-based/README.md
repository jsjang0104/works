# Workflow Description: Crowd-based

1. WMT24에 들어있는 번역물에 대해 두 가지 metric XCOMET-XXL 또는 MetricX-XXL로 QE score를 산출
2. QE Score (번역물의 품질)을 직접적인 Translation Difficulty Score (소스 텍스트의 번역 난이도)로 간주
3. WMT24에 들어 있던 human annotation (ESA)과 2.를 통해 얻은 Difficulty Score 추정치 간의  상관계수(DEC) 측정

# 파이썬 스크립트 기능
1. 대상 번역물 선택: 
   - `llms`: WMT24 공식 LLM 4종류 (Claude-3.5, GPT-4, Tower-70B, IKUN-C) -> Artificial Crowd
   - `true`: WMT24에 존재는 모든 시스템의 번역물을 취합하여 평균 산출 -> True Crowd
   - `ref`: WMT24 공식 정답 텍스트 (refA) -> 논문에 명시 
2. 메트릭 선택: `XCOMET-XXL` vs `MetricX-XXL` (각각 따로 실행 및 개별 DEC 계산)
3. 결과물 형식 CSV 저장 (`lp`, `src`, `avg_human_esa`, `numeric_score`) -> 해당 파일은 용량 이슈로 업로드 하지 않았으며, 다음 링크에서 확인 가능:
 - https://huggingface.co/datasets/HUFS-DILAB/reproduce-MT-crowd-xcomet-xxl-llms
 - https://huggingface.co/datasets/HUFS-DILAB/reproduce-MT-crowd-metricx-xxl-llms
4. 최종 DEC 산출, 터미널에 출력

# Final Results
## In this experiment
| mode | DEC score |
| :--- | :--- |
| Artificial(XCOMET-XXL) | 0.186 |
| Artificial(MetricX-XXL) | 0.170 |

## In the paper
| mode | DEC score |
| :--- | :--- |
| Artificial(XCOMET-XXL) | 0.177 |
| Artificial(MetricX-XXL) | 0.166 |

## What makes the final results different from the original?
- Translation models are different
