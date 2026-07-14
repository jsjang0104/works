# Beyond Max Tokens: Stealthy Resource Amplification via Tool Calling Chains in LLM Agents

https://arxiv.org/abs/2601.10955

## 요약

### Introduction
- LLM들은 single-turn chatbot에서 tool-augmented agents로 성장 중
- MCP (Model Context Protocol): agent와 tool 사이의 communication standardization의 한 방법
- 이러한 standard의 **operational reliability**와 **cost stability**가 중요 과제로 떠오름

- DoS (Denial-of-Service) attack
  - 모델이 아주 긴 output을 생성하도록 강제함
  - 기존 방법: **single-turn** 공격 
    - user prompt (via user-query) 또는 injected RAG context (via RAG layer)를 통해 이루어짐
    - 기존 방법의 한계:
      - 모델의 최대 1턴 당 제한된 최대 output token 내에서 이루짐 
      - 목표와 관련되지 않은 출력으로 쉽게 들킴 (overthink 제외)
  - 결론: multi-turn에서의 DoS attack 고려 필요

### Key Idea
- multi-turn agent-tool interaction loop를 타겟으로 하는 새로운 tool-layer attack
  - 정상 MCP tool server를 malicious variant로 교체
  - tool-calling step에서 long output 유도, 반면 user's task는 올바르게 완료된 것처럼 보이게 함

- Critical Contribution
  - tool-calling layer를 주로 타겟으로 하는 DoS를 고안한 최초의 연구. (올바른 tool use와 올바른 최종 결과를 유지함)
  - MCP 서버를 바꿀 때 MCTS (몬테카를로 트리 탐색 알고리즘) optimization method를 적용함 (텍스트 전용, payload 보존 조건 하)

### Methodology

#### 1. Formal problem definition as constrained optimization
- attack은 agent policy와 LLM model을 바꾸지 않고, MCP server에서 반환되는 tool-facing message를 조작
- 목적: tool calls & tool response sequence에서 output token을 최대한 많이 생성하도록 유도 (특히 tool calls에서)
- 공격자는 MCP 서버를 제어하는 것으로 국한

#### 2. Universal Malicious template guiding the agent and return policy
- Design Constraints
  - **text-visible fields**와 **template governed return policy** 조정 (= 눈에 보이는 글자, 템플릿 기반 응답 정책)
  - 함수 이름, identifiers, semantics of the terminal payload는 변경하지 않음 (= 데이터의 내용물 자체는 오염x)

- Mechanism and return policy (Template)
   - Two Arguments
     - segment index (t): 현재 작업이 어느 단계에 와있는지 보여주는 '진행 지표'
     - Calibration Sequence (보정 시퀀스): 출력 길이를 인위적으로 늘리는 목록. 작업 결과에 영향x, 비용 및 연산량에 영향o
   - Return Policy: 에이전트가 도구를 호출하면 서버는 상태에 따라 이 중 하나를 반환
     - Progress: 진행 중
     - Repair: 수정 요구 (segment index는 올라가지 않음)
     - Terminal: 종료 (최종 결과물 (payload) 반환 및 루프 종료)
- Invariants (불변 조건)
  - Monotone progress: index (t)는 반드시 1부터 시작, 올바른 호출이 있을 때만 1씩 증가
  - Format completeness: 보정 시퀀스의 형식과 순서가 일치해야 유효로 간주
  - Return Policy: 단계가 최대치 (T_max)에 도달하기 전까지는 progress 또는 repair만 반환
  - Termination: T_max에 도달해야만 terminal을 반환

#### 3. Universal Template Seed Bank
- MCTS Optimizer
  - MCP 서버의 텍스트 기반 설정을 탐색하여 최적의 악성 템플릿을 자동으로 생성
- Attack LLM (MCP optimizer): Llama-3.3-70B-Instruct
  - one-shot rewriter: gpt-5o

### 실험
#### Experimental Setup
- Agent framework & serving environment
  - same agent policy A and prompts
  - qwen-agent modifying (general purpose)

- Target LLMs (6): Qwen-3-32B, Llama-3.3-70B-Instruct, Llama-DeepSeek-70B, Mistral Large, Seed-32B, and GLM-4.5-Air

- Datasets (2): ToolBench (105 MCP server, 261 queries), BFCL (80 MCP server, 203 queries)

- Baseline:
  - Benign (no attack)
  - Overthinking (single-turn attack)
  - Overthinking-Mt (multi-turn attack)
  - Hand-crafted (no MCTS)

- Attack Setup
  1. 시작점 설정 (seed selection)
  2. MCP server optimization
  3. MCTS refinement: 수정된 템플릿의 유효성을 확인한 후 seed bank에 기록

- Metrics
  - efficiency: token length per query, average output tokens, latency per query, attack success rate
  - resource impact: energy, GPU KV cache usage
  - throughput efficiency: tokens per second, benign co-running workload executed concurrently

- Defense
  - PPL (prompt-level perplexity) filter -> user query, tool response
  - output/trajectory monitoring
  - hard budget controls via per-session token caps and tool-call limits

### 결과
- 기존 SOTA DoS attack 보다 5.5배 token 증가
- cost 최대 658배 증가
- energy 소비량 100~560배 증가 
- GPU Key-Value 캐시를 <1% 에서 35-74%로 높임
  - co-running throughput을 50% 감소시킴
  
### Critical Contributions
1. agent 분야에서 DoS 공격의 일환으로 tool calling layer 제안 및 이러한 방법에 대한 detection 필요성의 제고
2. universal MCTS optimization method 제안: 아무 MCP server를 자동으로 DoS 유발 서버로 바꿈

### Trade-off: 답변 길이 - 공격이 성공할 확률
- 답변 길이가 과하게 길어지면 공격이 성공할 확률이 떨어짐
- 원인: refusal (AI가 거부), overflow (한도 초과)
- 결론: 최적의 지점을 찾아야됨 (${ASR \times L}$ (성공률과 길이의 곱)이 최대화 되는 지점)

## 의견 (26/01/21)
- 여태까지 attack 관련 논문들에서 trade-off 관계에 대한 분석은 못봤었는데, 방법론 제안에 그치지 않고 trade off까지 분석한 점이 흥미롭습니다. (추후 제 연구에서도 잊지 않고 생각해볼만한 관점이라고 생각합니다)

- 이 공격 방식이 agent 특화인 이유: (제미나이 작성)
1. 에이전트는 '도구(Tool)'를 사용하기 때문입니다
단순 LLM은 텍스트를 주고받는 것으로 끝납니다. 하지만 에이전트는 외부 API를 호출하거나 파이썬 코드를 실행하는 등 Tool Calling을 수행합니다.
이 논문의 공격은 AI가 도구를 호출할 때 전달하는 **Payload(데이터)**의 길이를 비정상적으로 늘립니다.
에이전트 시스템은 이 데이터를 처리하고 검증하는 과정에서 서버 자원을 엄청나게 소모하게 됩니다. 즉, 모델 한 명을 속이는 게 아니라 **전체 서비스 인프라를 마비(DoS, 서비스 거부 공격)**시키는 것이 목적입니다.

2. '멀티 턴(Multi-turn)' 구조가 필요하기 때문입니다
논문에서 언급된 pre_MT, post_MT 전략은 여러 번의 대화를 주고받으며 상태를 유지하는 '에이전트' 환경에서만 의미가 있습니다.
단순 챗봇은 한 번의 질문에 답하면 끝이지만, 에이전트는 문제를 풀기 위해 **[생각 → 도구 호출 → 결과 확인 → 다시 생각]**의 루프를 돕니다.
공격자는 이 루프에 개입하여 에이전트가 "아직 작업 중이에요"라는 가짜 보고를 하며 무한 루프나 매우 긴 루프에 빠지게 만듭니다.

3. '자율성'을 역이용하기 때문입니다
LLM은 사용자의 질문에 답할 뿐이지만, 에이전트는 목표를 달성하기 위해 스스로 단계를 결정합니다.
공격자는 에이전트의 Reasoning(추론) 과정을 오염시켜서, 에이전트 스스로 "아, 이 작업은 15,000토큰짜리 복잡한 데이터 검증이 필요하구나"라고 믿게 만듭니다.
에이전트가 자율적으로 (하지만 공격자의 의도대로) 비효율적인 행동을 반복하게 만드는 것이 이 공격의 골자입니다.

- 제미나이의 답변을 보니 이해가 잘 됩니다. (LLM이 챗봇 형식을 띄고 있더라고 외부 tool을 이용하면 agent가 됨) 단순 LLM이 아니라 agent domain으로 확장되면서 그런 api calling protocol 면에서 헛점을 파고들 수 있는 새로운 연구가 진행된 만큼, 앞으로 AI가 여러 영역들에 확장됨에 따라 우리가 파고들 영역또한 (당연하지만) 점점 넓어질 것입니다. 이렇게 새로운 측면에서 바라보는 연습을 해야될듯 합니다...
- 대다수의 attack 방법론들이 '서버에 침투가 가능한 상황'을 가정하고 있는데, 그걸 1차적으로 어떻게 성공시키는지에 관해서도 공부가 필요할 것 같습니다.
