# POMDP Coder: LLM-Guided Probabilisstic Program Induction for POMDP Model Estimation

- **저자**: Aidan Curtis, Hao Tang, Thiago Veloso, Kevin Ellis, Joshua Tenenbaum, Tomas Lozano-Perez, Leslie Pack Kaelbling
- **arXiv**: https://arxiv.org/pdf/2505.02216
- **Submission Date**: May 2025
---

- 한줄 요약: 


## 1. Introduction

- POMDP provides a principled framework for modeling and solving problems, which is decision making under uncertainty, by explicitly representing uncertainty in **state perception, transitions, and rewards**. 

- Despite many prior works, practical application of POMDPs is bottelnecked by difficulties in **specifying accurate models of environments**

- In this paper, a critical challenge of **learning interpretable, low-complexity POMDP models directly from data** is addressed. 
    - POMDP components are represented as **probabilistic graphical models encoded by short probabilistic programs** using LLMs
    - Candidate probebilistic programs are evaluated against empirical observations and iteratively refined through LLM generated feedback.
    - 실험 결과, 논문에서 제시한 방법론이 significantly enhances sample efficiency compared to traditional tabular model or behavior learning methods and achieves greater accuracy than directly querying an LLM.
     

## 2. Related Work

- 여기서 집중하는 것: 
    1. methods that emphasize **extreme data efficiency** through the use of explicit models and representations
    2. methods that **use LLMs** to synthesize and refine these models

### 2.1 POMDP Model Learning

- challenge of learning POMDP models from experience: estimating the parameters of certain HMM is computationally intractable in general.

- Bayesian methods (such as Bayes-Adaptive POMDPs)
    - 방법: incorporate model uncertainty directly into decision-making by unifying *model learning, information gathering, and exploitation*
    - 단점: POMDP의 overall complexity를 증가시킴

- Optimism-based exploration algorithm
    - 장점: yields theoretical guarantees for efficient learning in specific POMDP subclasses
    - 단점: challenging to apply directly to real-world, complex domains

- Apprenticeship learning (도제 학습): 전문가의 시연을 보고 "어떤 환경이라면 저 순간에 저 행동을 하는 게 합리적일까?"를 거꾸로 추론하는 방법
    - estimate POMDP parameters by leveraging expert demonstrations
    - assumes that expert behavior encapsulates informative state-transition dynamics
    - 장점: helps reducing the burden of exploration
    - 단점: sensitive to the quality of the expert demonstrations

### 2.2 Probabilistic Program Induction


### 2.3 LLM Model Learning for Decision-Making


## 3. Background

### 3.1 POMDPs

### 3.2 Probabilistic Programs

### 3.3 POMDP Solvers


## 4. POMDP Coder

### 4.1 Learning Models


## 5. Experiments

### 5.1 Simulated Experiments

### 5.2 Baselines

### 5.3 Simulation Results

### 5.4 Real Robot Experiments


## 6. Discussion


## 7. Limitation