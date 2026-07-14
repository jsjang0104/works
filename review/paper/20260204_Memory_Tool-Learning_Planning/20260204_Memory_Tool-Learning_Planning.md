# Toward Efficient Agents: A Survey of Memory, Tool learning, and Planning

- https://arxiv.org/abs/2601.14192
- issue number #479
- 2026 Jan


## 요약

### 배경
- LLM을 이용한 agentic system이 최근 많이 발전됨

- 이전: information processing (perception, static text generation 위주)

- 현재: interacting with external environments to execute complex, multi-step workflows across diverse domains

- 하지만 그 과정에서 "**efficiency**"는 간과되어옴

- agent의 일반적인 workflow ([ ]안은 each iteration ${n}$을 의미함):
![alt text](images/479-2.png)


![alt text](images/479-1.png)
The evolutionary trajectory of efficient agent research. The diagram is organized into four principal
branches: Memory, Tool Learning, Planning, and Benchmarks (*흥미로운 figure라서 가져와봤습니다!*)

### Preliminaries
- Efficient LLM 연구는 많은 반면 efficient agent 연구는 별로 없음 -> 이 gap을 메워야...

- efficiency를 위한 세가지 논의
  1. **Efficient memory**: historical context 압축, memory storage management, optimizing context retireval
  2. **Efficient Tool Learning**: tool calls 횟수 줄이기, latency reducing (external interaction에서)
  3. **Efficient Planning**: executing steps, API call 횟수 줄이기

- "efficiency" characterize (trade-off의 관계에 있음): comparing effectiveness under a fixed cost budget, comparing cost at a comparable level of effectiveness

- LLM와 agent의 efficiencies의 차이는 무엇일까? (inference cost의 발생 관점)
  - pure LLM: 일반적으로 token generation에서 기인
  - agent: token geration 뿐만 아니라 tool invokeing, memory accessing, retries에서 기인

### 첫번째 논의: Efficient Memory
- memory-augmented reasoning: storing, reusing past experience

- agent memory의 efficiency
  - memory construction: summarization
    - working memory (inference time): textual memory (rewriting, compressing), latent memory (hidden activations, KV caches (보통 더 쌈->agent에게 attractive)), external memory (model 밖에 token-level로 저장되어있는 information) 
  - memory management
    - rule-based management: predefined rules for updating, removing, merging existing memories (static해서 이 과정은 inexpensive)
    - LLM-based management: decision form에 따라서 종류가 갈림
      - selecting from a discrete set of operation: model이 predefined set에서 action을 고름
      - generating open-ended updates: 모델이 직접 update를 수행
    - Hybrid Management: 약간의 rule-based + 선별적인 LLM-based
  - memory access: memory bank를 얼마 차지 안 하긴 함
    - memory selection: what/how to retrive memory?에 관한 것 (rule-enhanced/graph-based/LLM or Toll-based/Hierarchical/Training)
    - memory intergration: textual/latent
  - multi-agent memory
    - shared memory: centralizes reusable information (structured shared textual memory, latent shared memory)
    - local memory: retrieval, updates는 agent-local로 유지돼야됨 -> 메모리 관리를 위해 selctive writing, consolidation (통합), capacity control 등 고려 가능
    - mixed memory: shared + local memory

- Discussion
  - trade-off between memory compression and performance
    - memory extraction이 cost를 줄일 수 있는 것은 맞지만 critical information loss가 일어날 수 있음
    - 이것에 대한 해결은 open question (???머임)
  - online vs offline memory management: 이 둘 사이의 balance를 잘 맞춰야 된다

### 두번째 논의: Efficient Tool Learning
- Tool Learning의 efficiency
  - efficient for solving complex problems
  - reduces the cost of tool learning itself

- 주요 범주
  - Tool selection: tool retrieval literature의 세가지 종류
    - external retriever: 독립적인 모델
    - multi-label classification: fixed sized tool set에서 고르기
    - vocabulary-based retireval: tool이 special tokens로 embedding 되어 있음
  - Tool calling
    - In-Place Parameter Filling: model directly fills the tool's parameters during the response generation process. (CoT path 따라서...)
    - Parallel Tool Calling: 동시에 여러 task 수행 
    - Cost-Aware Tool Calling: cost가 tool calling model에게 줄 수 있는 reward의 한 종류가 될 수 있음
    - Efficient Test-Time Scaling: tree search-b ased searching strategies
    - Efficient Tool Calling with Post-training: post training에서 optimize (특히 RL을 primary mechanism으로)
  - Tool-intergrated Reasoning
    - Selective Invocation: TableMind라는 framework를 사용하여 tool을 반드시 필요할 때만 호출 (supervised fine-tuning 사용)
    - Cost-Aware Policy Optimization: RL을 optimization으로 사용

- Discussion
  - Tool-Intergrated Reasoning이 단순히 "enabling"이 아닌 "optimizing"을 가능하게 함
  - 미래 efficiency는 model's internal reasoning과 external tool envirionment를 어떻게 결합하는 것에 따라 갈릴 것

### 세번째 논의: Efficient Planning
- 핵심 철학: reasoning을 resource 제약 제어 문제로 간주

- Mechanism: *depth* of single-agent reasoning (via search and learning), *breadth* of multi-agent collaboration(via topology and protocol)을 optimizing

- Objectives: latency, token consumption, communication 제약 조건 아래에서 특정 task 성공시키기

- Primary paradigms
  - Single-Agent Planning: individual deliberation trajectories(개별 심의 궤적)를 최적화
    - inference strategy I: adaptive budgeting and contro
    - inference strategy II: structured search
    - inference strategy III: tast decomposition
    - learning-based evolution: policy optimization, memory and skill acquisition
  - Multi-Agent Collaborative Planning: 분산 시스템에서 협업 오버헤드를 최소화
    - Topological Efficiency and Sparsification (위상적 효율성과 희소화): communication 그래프 최적화
    - Protocol and Context Optimization: 전달되는 내용 압축, 프롬프트 기반 제약 조건
    - Distilling Coordination into Planning: collective intelligence를 단일 agent로 

- Discussion 
  - migration of computation from *online search* to *offline learning/structured retrieval*

### Benchmarks
각 목적에 맞는 benchmark 소개
*이 리뷰에 benchmark의 종류를 모두 나열하는게 의미 있을까 싶어서 benchmark의 목적성만 기재하였습니다.*

#### Memory
- Effictiveness Benchmarks
- Efficiency Benchmarks
- Efficiency Metrics in Memory Methods

#### Tool Learning
- Benchmarks for Selection & Parameter Infilling
- Tool Learning with Model Context Protocol
- Agentic Tool Learning

#### Planning
- Effectiveness Benchmarks
- Efficiency Benchmarks
- Efficiency Metrics in Planning Methods

## 의견
- 정보량이 매우..매우 많습니다.. 리뷰하는데 5시간 걸렸습니다 ㅎㅎㅎ
- memory에 대해서 다룰 때 너무 low level이라서 읽기 힘들었습니다... 하지만 efficiency를 위해 꼭 알아야될 개념이니 공부해두면 앞으로 좋을 것 같습니다!
- 이전에 읽었던 논문들이 배경 연구들을 간략하게 소개한다음에 novel한 방법론을 제시했었다면, 여기서는 배경 연구들을 아주아주아주 깊고 넓게 소개합니다
- 기존 연구에 대해 자세히 알기는 좋지만 이 논문에서 제시한 gap을 메우기 위해 novel한 기여가 있는가?에 대해서는 동의하지 못하겠습니다..