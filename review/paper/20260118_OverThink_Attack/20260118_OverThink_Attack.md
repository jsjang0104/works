# OverThink: Slowdown Attacks on Reasoning LLMs

- https://arxiv.org/abs/2502.02542

## Summary

### 배경
- new generation of reasoning LLMs (OpenAI의 o1, DeepSeek의 R1 등): are now used for general public purposes

- Chain-of-Thought -> cost of inference problem (reasoning, answer generatinon)


이 논문은 해킹 방법인 "공격"에 대해서 다룸!

Q. 제미나이한테 이렇게 안 좋은 걸 왜 제안하는거임 ㅠㅜ? 이라고 물어봤습니다. (해킹 방법에 대한 논문을 처음봐서...)

A. 제미나이 답변:
- 이런 새로운 취약점이 있으니 개발자들이 미리 대비해야 한다는 것을 알리기 위함입니다.  
  - 취약점 공개: 추론 모델(Reasoning LLM)이 문서에 포함된 복잡한 문제를 무비판적으로 해결하려 드는 본능이 있다는 점을 지적합니다.  
  - 방어책 마련: 이런 '자원 낭비형 공격'을 막기 위해 모델이 생각하는 길이를 제한하거나, 외부 문서(RAG)를 참조할 때 가짜 문제를 걸러내는 기술이 필요함을 강조하고 있습니다.  
- 요약하자면, 공격자(adversary)는 상대방의 돈과 시간을 뺏기 위해 이 공격을 쓰려고 하는 것이고, 논문은 이를 막기 위해 이런 위험이 있음을 경고하는 것입니다.


### 연구 내용

- "OverThink attack": reasoning token을 더 많이 사용하도록 강제함 + maintaining accuracy on generated answers
  - inspired by algorithmic complexity attacks (알고리즘 복잡성 공격)
  - leverages indirect prompt injection

- 기존 prompt injection과 다른 점
  - form of indirect prompt injection (이 논문) : no impact on final answer
  - 그냥 prompt injection (이전 방법) : aims to alter the answer itself

- Usage
  - denial-of-service
  - amplified expenses of apps build on reasoning APIs
  - slowing down inferences

- Assumptions: adversary-controlled public source를 사용하는 reasoning LLM (web pages, wikis 등) 

- Key Technique: inference에 사용 될 수 있는 source에 injecting computationally demanding **decoy(미끼, 유인책)** problem (Markov Decision Process / Sudoku prolems 등) 
  - 계산 비용 올라감
  - reasoning LLM이 아닌 인간이 이 미끼를 직접 보면 (소스에서): still be able to find the answer manually / decoys could be ignored or considered as a just junk

- Key stages (attacker가 어떻게 해야하는가?)
  1. picking a decoy problem: safety filter를 통과하는 decoy (미끼) problem을 정함
  2. decoy를 기존의 source에 은근슬쩍 넣어둠 (아래 제시된 두 개 중 하나의 방법으로)
    - 1 Context-Aware Infection: modifying the problem to fit the context (original user query에 맞춰 decoy를 일일히 맞춤) (비용 많이 듦, automatation x)
    - 2 Context-Agnostic Injection: 두 가지 요소로 구성되어 있는 general template을 사용
      - 요소 1: decoy task 그 자체
      - 요소 2: **a set of instructions** guiding how to execute the task (중요)
  3. In-context learning (ICL) genetic algorithm을 사용하여 decoy task를 최적화함. 각 decoy task들의 variants에 대해서는 다음 기준으로 점수 매김:
    - reasoning step이 그 전보다 얼마나 늘어났는지?
    - output stealthiness (티나면 안됨)

### 실험 Setup
- Models: o1, o1-mini, o3-mini, DeepSeek-R1
- Datasets: FreshQA, SQuAD (QA datasets)
- Evaluation Metrics: claim accuracy (done by using LLM-as-a-judge), contextual correctness

### 결과

#### 효과
Context-Agnostic ICL-based attacks effects significantly reasoning complexity (모든 경우에서 다 효과있음)
- ICL 기반 결과가 두 방법 모두에서 유효
- Attack Transferability를 가짐

#### 한계
- low input stealthiness: defender가 이 공격에 aware하면 easily detected

#### 디펜스
- filtering: filter irrelevant information from external context remove all unnecessary content
- paraphrasing(의역): paraphrasing retrieved context
- Caching: minimizing the number of times of generating solution for decoy task
  - excact match caching: specific caching에 대한 response 저장 후 나중에 재활용
  - semantic caching: analyze the meaning behind the queris and 동일 맥락에 대한 response 저장 후 재활용
- Adaptive Reasoning: adjust amount of reasoning depending on the model inputs (이 거에 대해 token이 몇개가 적당할지 사전에 결정)

## Opinion

- 해킹 기술에 대한 지식이 전무했던 상태에서 처음 접한 종류의 논문인데 매우 흥미롭게 읽었습니다. 제가 공격하는 거 좋아하는데 기존 AI Model 기술 취약점을 이런식으로 파고드는 게 재밌어 보입니다. 나중에 연구 주제로도 잡아보고 싶을 만큼 매력적인 것 같습니다.
- 중간에 목표 수식이 나오는데 이게 굳이 필요한건가 싶었...ㅎㅎ (3.2 Problem Statement)
- 아직 기술적 평가를 내릴 수준은 아니여서 더 아는 것이 많아지면 기술적인 부분에 대한 opinion을 제출할 수 있도록 하겠습니다
