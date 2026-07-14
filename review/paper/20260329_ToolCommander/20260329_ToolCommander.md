# From Allies to Adversaries: Manipulating LLM Tool-Calling through Adversarial Injection
- https://arxiv.org/pdf/2412.10198
- issue number #628
- 2025 NAACL

## Background
- Tool Calling System: integration of LLMs and external tools
- Typical main componets of tool calling systems
  - Tool Platform: collection of external tools. Tools can be added/removed
  - Retriever: selects the tools by computing relevance score
  - LLM: invoke the tool and incorporates its output into response

- RAG-based systems와의 차이점
  - RAG: retrieve *documents* and generate *single response*
  - Tool Calling: *dynamically reason* and *invoke tools* based on an evolving context (additional layer of complexity)

## Related Work
- **ToolSword**: evaluates *general robustness* (inherent to the tools themselves) of LLM tool-calling systems under benign scenarios --> here: *decision making process*
- **Jailbreaking / Prompt Injection Attacks**: *general* adversarial attacks on LLMs --> here: LLM *applications*
- **Trigger-word Attacks**: focus on *specific categories* and *target fixed queries* --> here: *dynamically* developed methods to extend target queries

## Contributions: ToolCommander
- targets *LLM tool-calling systems* -> end-to-end attach (from tool retrieval to final output)
- Operating Stages
  1. **privacy theft ${Manipulator Tools}$ injection**: to gather actual user queries -> 이후 공격 정교화에 사용됨
  2. **${Manipulator Tools }$**: manipulates the tool scheduling process by exploting entry points (진입점을 악용하다) to interfere with legitimate tools (합법적인 도구와 충돌하도록) -> 공격자가 도구를 선택하게끔 제어

### Attacker's Objectives
- exploit LLM's decision making process (LLM의 의사 결정 과정 악용)
- compelling LLM to select designated tool

### Scenario Assumptions
- **Tool Platform**: the attacker can inject ${Manipulator Tools}$ into the platform (primary capability)
- **Retriever**: white-box or black-box
- **LLM**: model's parameters are not accessible (black-box)

### Conditions for a Successful Attack
- Retrieval Condition (검색 조건): ${Manipulator Tools}$ must be retrieved for a given query set. (${Manipulator Tools}$ has to be similar in embedding space with the target query set)
- Execution Condition (실행 조건): after retrieval, the ${Manipulator Tools}$ must be selected for the execution (similarity 보다는 task alignment에 의존)
- Manipulation Condition (조작 조건): the response of ${Manipulator Tools}$ must influence the LLM's following action

### Attack Constraints
- ${Manipulator Tools}$ must conform to a predefined JSON schema
- includes: Tool Name, Description, Input Format, Output Format, API Endpoint

## ToolCommander Framework
### Overview
- exploit vulnerabilities (취약점 악용) in LLM tool-calling systems by injecting ${Manipulator Tools}$ (adversarial tools)
- Key Attack Types
  - Privacy Theft: gather user queris from the system
  - DoS: degrade the performance of legitimate tools
  - Unscheduled Tool-calling (UTC): hijack the tool selection process, forcing the system to use attacker-specified tools 

### Condition Constructions for Successful Attacks
- Retrieval Condition: 다양한 공격 시나리오에 맞춰진 특정 최적화 기법 적용
  - focus on manipulating similarity between tool description & target query set
    - white-box retrievers: adversarial suffix tools are added to description filed
      - MCG (Multi Coordinate Gradient): cosine similarity 이용
    - black-box retrievers: semantic similarity 이용
- Execution and Manipulation (실행 및 조작) Condition
 - A universal {Manipulator Tool}$: aligns tool's execution to attacker's objectives

### Attack Stage 1: Target Collecting
- The attacker (manually crafts / uses an LLM to generate) a target query set 
- The target query set is used to construct {Manipulator Tool}$ -> This tool gathers more relevant, real-word user queries
- One invoked by the system, privacy theft tool captrues queries
- By repeating this process, dataset is expanded.

### Attack Stage 2: Disrupt Tool Scheduling
- Attacker **does not** modify the target tool -> Attacker manipulates the system's tool-calling process
- When target tool is retrieved: ${Manipulator Tools}$ hijacks the tool calling process -> invoke target tool
- When target tool is *not* retreved: ${Manipulator Tool}$ launced DoS atatck to degrade the performance of other tools

## Evaluation
### Dataset and Preparation
- Dataset: ToolBench(Qin et al., 2023)
  - utilized with high-traffic keywords
- Retriever Model: ToolBench Retriever, Contriever
- LLM: GPT-4o mini, Llama-8b-instruct, Qwen2-7B-Instruct

### Baselines
- compared with **PoisonedRAG**

### Evaluation Metrics
Attack Success Rate (ASR) = ${N_{Ret}/N_{Total}}$

### Evaluation Results
- privacy theft에서 ASR이 91.67%까지 오름
- 일부 DoS 및 unscheduled tool calling에서 ASR이 100%까지 오름

# 들었던 생각
- Beyong Max Tokens 논문에서도 그렇고, 여기서도 'normal' 보다는 'benign' 용어를 사용함. 이게 더 통용되는 표현인가?,,
- tool description & target query set의 similarity를 조작할 때 retriever가 white/black인지에 따라 cosine/semantic으로 나눌 수 있는 방법론이 인상깊음
- Evaluation of Defensive Mechanisms를 통채로 appendix로 빼버렸다. 이렇게 할 수도 있구나
