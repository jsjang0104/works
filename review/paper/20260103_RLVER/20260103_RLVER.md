# RLVER: Reinforcement Learning with Verifiable Emotion Rewards for Empathetic Agents

----

**Author:** Anonymous (for blind review)  
**Journal/Year:** Under review as a conference paper at ICLR 2026

----

## 세 줄 요약

1. 모델에게 empathetic reasoning 가르치기 
2. 기존 SAGE framework(LLM-powered simulator that mimics human-like emotional responses & inner reasoning) -> RL에서 environment로 활용
3. 성능 굿~

## 들었던 생각

### 필요 역량

- Evaluation benchmarks 공부 필요: SAGE 등

- RL 알고리즘에 대해 공부 더 필요: PPO, GRPO 등

### 연구 아이디어

- 모델에게 empathetic reasoning을 가르칠 때 방법?: Multimodal로 접근해서 (ASR model을 활용) speech와 text를 만들어냄 -> 훈련 대상 모델이 training할 때는 data를 text로만 사용 -> 정답지는 speech data에 있는 emotion

- 논문에서 계속 강조하다 싶이 RL model에게 줄 **정량적인** reward가 필요함:
  - 논문에서와 같이 가상 reward 환경 정의시: reward를 정량적으로 줄려면 model이 내놓은 답변에 있는 "emotion"도 정량적으로 평가할 방법이 필요 -> 논문에서 쓰인 것과 다른 방법이 있을지??
  - 가상 환경 x 실제 인간: 인간 프롬프트를 어떻게 정량적으로 정의할까??? (주변 사람들을 보면 -> 생각보다 llm를 매우 감정적으로 대함)

### 교수님께 질문드리고 싶은 부분

이 논문에서는 모델의 core capabilities를
  - empathic depth
  - core insight
  - solution crafting
  - style adaptability
  - dialogue guidance
이렇게 5가지로 정의하고있고, 이것들에 대한 evaluation criteria가 페이지 17~21페이지에 거쳐서 나와있습니다. 
그런데 생각보다 매우 정량적이지 않은 기준이어서 살짝 놀랬습니다. (reward model이 reward는 주는 방식은 매우 정량적으로 수학적으로 정의되어 있는 것에 비해서요...) 이 criteria를 교수님께서는 어떻게 생각하시는지 궁금합니다!

## 1. Introduction

### 기존 문제

- LLM들은 수학, 코딩, 알고리즘 같은 분야에 강한데 비해 social, emotional reasoning은 약함 (인간은 IQ, EQ 둘다 유)
- 기존 방법: supervised fine-tuning / rule-based template
  - 이런 방법들은 data scarcity, rigid dialogue structure, limited generalization과 같은 문제 유
- RLVR for enhancing dialog capability가 직면하고 있는 문제점
  - conversational rollout를 형성할 수 있는 환경
  - consistent, verifiable emotion reward design

### 제시된 방안

- RLVER frame work 정의
  - 최초 end-to-end reinforcement learning framework
  - verifiable emotion rewards, SAGE framework 활용
- agent가 emotion score emitting -> simulated user updates emotional states
- 명시적인 '생각' 스텝 보이게 함

### 성과

- Sentimentent-Benchmark score: 13.3 (기존) -> 79.2 (본 논문)
- 수학, 코딩 능력은 유지
- 생각 모델: 공감, 직관 / 생각x 모델: 행동 지향
- open source로 공개되어 있음

## 2 Reinforcement Learning with Verifiable Emotion Rewards

### 2.1 Emotion Rewards from Self-Consistent User Simulation Engine

- Reliable reward signal이 필요함 -> dynamic, scalabe, psychologically-grounded environment가 필요
  - 기존: static datasets / simple LLM-as-a-judge (they fail to capture the use's evolving emotional state)

- SAGE (Sentient Agent as a Judge) framework 활용 
  - Sentient Agent: LLM-powered simulator that mimics human-like emotional responses & inner reasoning
  - Multi-hop reasoning
    - Simulate Emotion Change: The agent assess how the response made it feel, updating **numerical emotion score** -> interpretable **inner thoughts**
    - Generate a Coherent Reply: 새 감정 상태에 맞춰 대화를 이어나가기 위한 response 생성

- 이 연구에서는 이 SAGE framework를 live training environment로 활용함
  - Sentient Agent = user simulator
  - emotion score = reward signal for RL

- Opacity pitfalls (보상함수 불투명성): user simulation engine S의 deterministic emotion scores 사용 -> 해석가능한 proxy 정의 (수식..)

### 2.2 Heart-in-the-Loop Reinforcement Learning

- Closed Feedback Loop 정의: LLM alternates between '감정 답변 생성' - 'simulation engine으로부터 피드백 반영'

- 단계
  1. 가상 유저 엔진 S가 몇개의 Sentient Agent를 구체화 (성격, 배경 등)
  2. 훈련 모델 - Sentient Agent 대화
  3. S가 2개 output compute
    - verifiable emotion score (based on the inference of internal emotional state + explicit reasoning)
    - updated emotional state기반 new reply
  4. 순서(기존 정의)를 넘기거나 emotion score가 특정 threshold 이하로 떨어지면 종료 (사회적 매장이야!)

- Policy Optimization (PPO) 사용
  - an on-policy algorithm suited for high-variance environments like LM
  - PPO maximizes a regularized expected reward object 
  - (PPO objecitve function 수식...)
  - 사용 시 장점: clipped surrogate loss로 safer exploration, smoother convergence

- Group Relative Policy Optimization (GRPO) 사용
  - optimize for long-term dialogue
  - learning sequence-level strategies with group-level advantage estimate

- modestly aligned checkpoint로 initilalized된 model 사용 (pre-trained)

## 3. Experiment

### 3.1 Experimental Setup

- Base Model: Qwen2.5-7B-Instruct (fine-tuned x)
- Training Strategy: (1) think, then say (2) direct reply (prompt는 Appendix에 명시)
- Training Enviroinment and Reward
  - SAGE framework 
  - emotional goal 달성 / max 8 turns
- 500 supportive dialogue scenarios / 8 diverse user goals (topics 다양) (prompt는 Appendix에 명시)
- Baselines: model comparison (SOTA랑)
- Evaluation Banchmarks: SAGE benchmark, Chit Chat setting (extendes SAGE beyond emotional topics)

### 3.2 Main Results

- RLVER: 경량 모델을 near-frontier model수준까지 끌어올림
- '생각하는' 모델이 더 감정을 잘 다룸
- GRPO: greater training stability, PPO: higher performance ceiling
- Empathetic reasoning: general capability에 영향 별로 없을 무

### 3.3 Qualitative

- core capabilities: 
  - empathic depth
  - core insight
  - solution crafting
  - style adaptability
  - dialogue guidance

- employs LLM-as-a-judge 

- RLVER가 다섯가지 영역에서 improve
- '생각'모델: empathy and insight / '안 생각' 모델: action
- PPO 어떤 거에 특화 / GRPO balanced and stable

### 3.4 Impact of Training Environment and Reward

- 어려운 환경일 수록 좋은 결과는 x
- thinking model: robustness to 환경 변화

## 4. Related Work

- 감정 지원 대화 연구: 대부분 지도 학습 의존, RL을 적용한 선행 연구는 없었음

- Zero RL: pre-trained LLL에 중간 fine-tuning 없이 직접 RL 적용

## 5. Conclusion

- 인간 labeling 없이 중간 규모 LLM으로도 emotional intelligence 습득 가능을 보여줌

- 핵심: simulator(that generates verifiable emotion rewards), 잘 선택된 훈련 전략, RL 알고리즘, 환경, 리워드 디자인 