# OptimalThinkingBench: Evaluating Over and Underthinking in LLMs 
- issue number #531
- https://arxiv.org/pdf/2508.13141
- meta, 2025 10월

## 요약

### 배경
- 목적에 따라서 thinking/non-thinking model이 따로 있음
  - thinking -> complex tasks (slower, expensive)
  - non-thinking -> simple tasks (faster, cheaper)
- 사용자들이 어떤 모델을 쓸지 스스로 정해야됨

### Key Contribution
#### **optimally-thinking models** 개발을 위한 방법론인 **OptimalThinkingBench** 제안
- jointly evaluates overthinking & underthinking in LLMs
- performance & efficiency balance가 맞는 optimally-thinking models를 개발할 수 있게 도움을 줄 수 있음
- 2개의 sub-benchmarks
  - **OverthinkingBench**
    - 두 가지 subsets:
      - OvT-Math (math: MATH dataset의 level 1, 2 problems)
      - OvT-General (general queries: constrained dataset generation -> dataset filtering 순서 pipeline으로 만듦)
    - fully synthetic dataset creation recipe을 지킴 (나중에 easily extended/adjuested)
    - non-thinking model에서 accuracy가 더 높음
    - 예시: which layer in atmosphere protects us from UV radiation?
    - OverthinkingBench에 대하여 새로운 evaluation metrics 하단 제시
  - **UnderthinkingBench**
    - 11 challenging reasoning tasks from 6 different domains (games, algorithms, graphs, arithmetic, geometry, logic) + 2 competition math
      - Reasoning Gym
      - 4 standard math benchmarks
    - 아무리 작은 thinking model이라도 그 모델이 large non-thinking model보다 accuracy가 더 높을 때의 데이터셋만 취급함
    - 예시: Find the shortest path in the following maze
    - UnderthinkingBench의 Accuracy 평가에 관하여는 기존에 존재하던 방법론 사용
  - **OptimalThinkingBench**: F1 score 사용
    - over/underthinking progress를 single unified metric으로 평가하기 위함
    - overhtinking bench에서 AUCOAA(하단 서술)를, underthinking bench에서 Acc_ut 사용

    ![alt text](images/531-1.png)

#### novel thinking-adjusted accuracy metrics 제안: Overthinking-Adjusted Accuracy (OAA) for OverthinkingBench
- 오답 분류 방법
  - 수학: answer matching
  - 다른 domain: LLM for correctness judgement

![alt text](images/531-2.png)

- 위 지표를 사용하여 OAA 곡선 아래 면적인 AUCOAA를 계산 
  - t_max: pre-defined maximum number of thinking tokens
  - 그래프 아래 면적이 더 넓을 수록 좋음

![alt text](images/531-3.png)

### 실험 및 결과
- 33 models
- **no model is able to optimally think on our benchmark**
  - thinking models: often overthink without performance improvement
  - non-thinking models: often underthink 
- 모델이 어떻게 under/overthink를 하는지에 대한 qualitative & quantitative 분석

### 추가 연구
- training time & test time approaches to optimal thinking

- 1. **reward shaping**: OverthinkingBench에서는 성능 올랐지만 (token reduced), UnderthinkingBench에서 accuracy가 너무 떨어짐
  
- 2. **routing** between thinking and non-thinking models based on the question difficulty (router model을 따로 두고 생각을 할지/말지 판단): 성능 향상은 있지만 oracle model(이상적인 목표)에 비해서는 한참 멀었음
  
- 3. **deliberate prompting**: 대놓고 overthink 해라/말라 명시
  - "dont overthink" -> 효과 굿
  - "let's think step-by-step" -> accuracy 하락 부작용


## 들었던 생각
- 추가 연구에서 세 가지의 번뜩이는 아이디어로 열심히 연구하신 것 같은데 뚜렷하게 효과적인 결과로 귀결되지 못한게 마음이 아프다
- 추가 연구 파트를 읽기 전에 내 머릿속에 있던 생각은 routing에 제일 가까웠다. 그런데 추가 연구 내용을 읽고 나니 deliberate prompting이 가장 더 연구해보고 싶은? 관심가는 내용인 것 같다. (직관적이라서...)
- 특정 목적을 위한 novel benchmark selection 및 evaluation metrics를 어떻게 연구해야되는지 감을 잡게 해주는 논문인듯
