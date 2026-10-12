# Synthesizing world models for bileval planning

- **저자**: Zerg Ahmed, Joshua B. Tenenbaum, Christopher J. Bates, Samuel J. Gershman
- **arXiv**: https://arxiv.org/pdf/2503.20124
- **Submission Date**: July 2025
---

## 1 Introduction

- Video games는 좋은 testbed임
    - RL은 게임에서 좋은 능력을 보였음 (Atari 등)
    - 하지만 인간보다 못함 (특히 variation에서 generalize 못함)

- 최근 LLM 등 foundation model들이 game-playing agents로 쓰임
    - world knowledge로 강한 reasoning 장점
    - 그러나, 예시가 주어지지 않거나 domain이 너무 training set에서 멀면 못함

- 인간이 배우고 계획하는것은 foundation model이랑 end-to-end RL model들이랑 확실히 달라보임
    - 그래서 우리는 인간한테 영감을 받아서, algorithm을 개발할거임
    - 인간은 prior knowledge를 이용해서 새 게임을 함
    - 인간이 structured causal models (=theories)를 배우고, 그걸 planning and exploration에 쓴다는게 *TBRL (theory-based reinforcement learning)*
    - model-based RL에 비해서 TBRL은 motor skills and precise timing에 대해 잘 배우지만, extensive exploration을 필요로하는 domain에서는 약함
    - 인간 인지를 더 강하게 모방하여 이런 gap을 채울 수 있을겨

- Tsividis et al. (2021)은 TBRL을 EMPA 에이전트로 concept proofing을 했음
    - EMPA는 비디오 게임의 rule을 domain-specific language (VGDL)로 배움 
    - Atari-style video games에서 성능 굳

- 하지만 TBRL은 아직도 remains challenging: 현존 TBRL은 두가지 major limitation을 가짐
    1. 그들의 theory languages are restricted to domains that can be represented in VGDL. (반면 인간은 다른 kinds도 잘하쥬?)
    2. TBRL agents가 쓰는 planning algorithm은 not scalable to large state spaces (value-based iteration에 의존하기 때문 -> 차원의 저주 when computing the value for large state-action pairs)

- 우리 논문에서는 TBRL을 새 알고리즘 테크닉으로 extend함 -> 그럼 agent가 more skilled and flexible and tractable 할 수 있음
    1. 장점 1: reusing previously learned, high-level symbolic abstract concepts, adapting them to the particulars of a new domain via a fast-learning mechanism based on **program synthesis**
        - 이러한 high-level abstraction은 planning operators를 포함함 -> 만약 에이전트가 low level details를 빨리 채울 수 있다면  useful concepts를 재활용할 수 있는 것 (매번 새로 배울 필요 없)
    2. 장점 2: much richer set of world model을 얻을 수 있음
        - VGDL이 아니라 Python으로 (아주 expressive!)
        - 이게 되는 이유는 LLM이 있어서

- 미안하다 이거보여주려고 어그로 끌었다: "TheoryCoder"

## 2 Related Work

### 2.1 Theory-based RL

#### 2.1.1 Human Learning

#### 2.1.2 Human learning principles missing in Deep RL

#### 2.1.3 Limitations of current Theory-Based RL systems

#### 2.2 Model-based reasoning

#### 2.2.1 Neural Models

#### 2.2.2 Symbolic Models

#### 2.2.3 Synthesizing models using LLMs

### 2.3 Bilevel Planning

### 2.4 LLMs for planning and low-level policies

## 3 Theory Coder

### 3.1 Overview

### 3.2 Preliminaries

### 3.3 Theory language

#### 3.3.1 High-level planning and abstractions

#### 3.3.2 Low-level Python transition function and planning

### 3.4 Learning

### 3.5 Summary

## 4 Experiments

### 4.1 Evaluation and Metrics

### 4.2 Environments and Tasks

### 4.3 Results 

### 4.4 Role of Abstraction Design

### 4.5 Overall Sample Efficiency and Progress Across Domains

### 4.6 Behavior Comparison

### 4.7 Analysis of Robustness and Failure

### 4.8 Excluding Training Data Contamination

## 5 Conclusion