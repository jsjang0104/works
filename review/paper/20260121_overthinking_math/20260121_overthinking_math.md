# Do {NOT} Think That Much for 2+3=? On the Overthinking of Long Reasoning Models

https://openreview.net/forum?id=MSbU3L7V00&noteId=rqP87e9HLl

## 요약
long reasoning model이 math 문제를 풀 때의 overthinking에 대해 분석 metrics와 해결 방법을 제안하는 내용입니다 

### 배경
- scaling test-time compute: allocates more computational resources
  - CoT (Chain of Thoughts)
  - multiple strategy exploring
  - complex step 수행
  - doulbe checking 수행
- long reasoning model에서 overthinking이 문제될 수 있음
- 이때 할 수 있는 질문: "우리는 효율적이고 똑똑하게 test-time compute를 scaling하고 있는가?"

### Key Idea
#### Overthinking Issue 분석

1. 분석 방법
  - 1). 모델 응답의 distribution
  - 2). 응답에서 두가지 inefficiencies 분석 - accuracy에 대한 기여가 없음, diversity가 없음
  - 3). empirical 분석

2. Long reasoning models exhibit significant **over thinking** issues, particularly with **easier math problems**
  - “what is the answer of 2 plus 3?"와 같은 매우 간단한 물음에도 long reasoning model은 일반 모델보다 20배 이상의 token을 사용
  - overthinking patterns
    - (1) contribute minimally to improving accuracy
    - (2) lack diversity in reasoning strategies
    - (3) occur more frequently with simple problems

3. 좋은 Reasoning은 다음 두 가지 조건 **모두**를 만족해야됨
  - accuracy
  - 문제에 따라 적절하게 설정된 level의 complexity

#### 제안 (위 문제를 해결하기 위하여)
1. overthinking을 완화하고 추론 과정을 단순화하는 **전략** 제안    
  - 모델이 더 간결한 응답을 생성하도록 가르치는 self-training paradigm
  - 자체 생성된 출력물을 간단하게 만드는 방식
  - three key steps
    - 수학 데이터셋에 대해 long reasoning trace 생성
    - 그 traces에서 필요 없는 부분을 걷어냄
      - First-Correct Solutions: 첫번째 정답이 나올때까지의 부분만 사용
      - FCS + Reflection: 첫번째 + 두번째
      - Greedy Diverse Solutions: 두번째 정답이 novel reasoning을 할 때만 인정 (diversity를 위하여...)
    - 간결화된 것을 갖고 preference optimization training 수행   
      - (short, long) reasong pairs 활용
      - DPO, RPO, simPO, SFT 활용

2. computational resource를 'outcome'과 'process' 두 가지 관점 모두에서 합리적으로 쓰는지 평가하기 위한 novel efficiency **metrics** 제안
 - Outcome Efficiency Metric: 간결화된 solution이 accuracy 향상에 얼마나 영향을 주었는가?  
 ![alt text](images/436-1.png)
 - Process Efficiency Metric: 간결화된 solution이 diversity에 얼마나 기여했는가?
 ![alt text](images/436-2.png)


### 실험 및 결과
- Reduces computational overhead while preserving model performance
  - token output을 44.5%까지 줄임 (MATH500 -> QwQ-32B-Preview에서)

![alt text](images/436-3.png)

## 의견
- 이 논문 맛있네요..
- 한가지 논문 내에서 overthinking 이슈 분석, metrics 제시, 완화 방법 모두를 분석한 점이 매우 인상 깊습니다 
- 매우 많은 양이 들어있음에도 불구하고 methology 자체가 직관적이게 기술되어 있어서 좋습니다
- 그리고 (제 기준에서) evaluation metrics와 해결 방식이 novel하게 느껴집니다
- 데이터셋이 모두 STEM 기반이고, 논문 내용 자체도 math에서의 overthinking을 다루고 있어서 다른 domain에서도 연구가 수행되면 좋을 것 같습니다
