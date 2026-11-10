---
title: "Efficient Estimation of Word Representations in Vector Space"
authors: [Tomas Mikolov, Kai Chen, Greg Corrado, Jeffrey Dean]
journal: "arXiv:1301.3781"
year: 2013
tags: [NLP, WordEmbedding, VectorSpace, Word2Vec, CBOW, Skip-gram]
reviewed_by: "Jisoo Jang"
date: "2025-11-07"
---

# Efficient Estimation of Word Representations in Vector Space
> [!NOTE]
> **저자:** Tomas Mikolov, Kai Chen, Greg Corrado, Jeffrey Dean
> **학회/연도** arXiv:1301.3781/2013

---

### 1. 한 줄 요약 (TL;DR)
복잡한 non-linear hidden layer를 제거한 Word2vec mode (CBOW, Skip-gram)과 output layer 최적화 방법론(hierarchical softmax, negative sampling)을 통해 단어 벡터간 linear regularity(syntactic, semantic 관계)를 입증



### 2. 이 논문이 해결하려는 문제 (Problem Statement)
- 기존의 모델(NNLM, RNNLM) 구조: input layer - projection layer - hidden layer - output layer
- 목적: NNLM(N개의 단어에 대해 다음 단어의 확률 예측), RNNLM(가변적인 단어 갯수(문맥)에 대해 다음 단어의 확률 예측) 
- 기존의 모델에서 training example 하나 당 시간복잡도: **(N X D) + (N X D X H) + (H X V)** (N: word vector개수, D: word vector의 차원 수, H: hidden layer의 차원 수, V: vocabulary size) 
- 이 때 dominating term은 hidden layer에서 output layer로 가는 계산 (계산량이 너무 많아짐)
- 따라서 이 논문의 목적은 word vector의 linear regularity는 유지하면서 계산량을 줄이고, accuracy는 늘리는 것



### 3. 핵심 아이디어 및 방법론 (Key Idea & Methodology)
**Word2Vec**의 혁신

#### 1. **nonlinear hidden layer 없이 단순한 projection layer만 있는 CBOW, Skip-gram 구조**
NNLM/RNNLM: **단어 예측**이 목표 (단어 벡터 학습은 단어 예측을 위한 수단)
word2vec(CBOW, Skip-gram): **단어 벡터 학습**이 목표 (단어 예측은 단어 벡터 학습을 위한 수단)

1. **CBOW**: 주변 단어들의 값을 averaging(평균내기)하여 중심 단어 vector 1개를 학습 (주변 단어 정보들이 합쳐지기 때문에 개별 정보들의 일부 손실 가능성 있음)
- 1. {cat, ___, on}을 모델에게 줌
- 2. cat, on 벡터를 랜덤한 값으로 초기화
- 3. cat, on 벡터의 평균을 내고 정답일 확률 계산 
- 4. 이 확률과 실제 정답(sat)의 확률 비교 후 주변 단어 벡터 값들과 학습에 쓰인 parameter값을 수정 (back propagation)

2. **Skip-gram**: 중심 단어를 projection(투영)하여 주변 단어 vector C개를 학습 (개별 정보 손실이 없지만 학습 시간이 더 오래걸림)
- 1. {sat}을 모델에게 줌
- 2. sat 벡터를 랜덤한 값으로 초기화
- 3. 주변 단어 벡터 C*2개를 예측하여 확률 계산
- 4. 이 확률들과 실제 정답 (cat, on)의 확률을 C*2번 비교 후 이 값들을 모두 합쳐서 중심 단어 벡터 값과 학습에 쓰인 parameter값을 수정 (back propagation)

#### 2. Output Layer의 최적화 (Hierarchical Softmax, Negative Sampling)
1. **Hierarchical Softmax**:
- V개의 단어를 잎(leaf node)으로 가지는 이진 트리
- 트리의 루트 단어에서 특정 단어까지 가는 유일한 경로의 확률을 계산 (모든 V개의 단어와 일일히 비교x)
- 중간 노드에서는 시그모이드를 사용하여 왼쪽/오른쪽 확률을 계산
- 기존 standard softmax의 vocabulary의 크기만큼(V)의 계산량 -> log2V의 계산량 (binary classification)
- tree의 모양에 따라 balanced, huffman(실제 단어 분포에 따름. unbalanced)으로 분류하며 보통 후자를 더 많이 사용

2. **Negative Sampling**:
- 기존 model에서는 모든 가능한 단어(V)에 대한 확률을 계산 (normalized)
- NS에서는 모델에서는 확률이 아닌 정답/오답의 binary classification 계산 (not normalized)
- 진짜 정답과 무작위로 뽑은 가짜 정답(negative sample) 끼리만 비교
- 모든 단어V개 에 대한 확률의 합이 1이 되어야 한다는 정규화 개념이 없음



### 4. 주요 실험 및 결과 (Experiments & Results)
- dataset: 5 types of semantic questions(8869), 9 types of syntactic questions(10675)
- 평가 지표: question type 각각에 따른 accuracy (synonyms 고려 x -> 100% accuracy impossible)
- DistBelief framework 사용 (mini-batch asynchronous gradient descent, adaptive learning rate, 50~100 replicas)

#### 같은 Training data set(Google News 6B tokens), 640-dimensional word vectors로 실험했을 때 성능(%)
- Semantic accuracy: Skip-gram(59) >>>넘사벽>>> CBOW(24) >= NNLM(23) >>> RNNLM(9)
- Syntactic accuracy: CBOW(64) > Skip-gram(59) > NNLM(53) >>> RNNLM(36)

#### Microsoft Sentence Completion Challenge 성능(%)
- Skip-gram + RNNLMs(58.9) > RNNLMs(55.4) > Skip-gram(48) ...

#### word vector의 Linear Regularity 발견:
- vector operation으로 단어 벡터의 syntactic, semantic 관계 입증 가능성 발견
- Vector('King') - Vector('Man') + Vector('Woman') ≈ Vector('Queen')
- 모델이 '남성:여성','국가:수도'등 같은 다양한 관계를 학습


### 5. 이 논문의 장점 (Strengths / Contributions)
- 새 model architecture 제안: 기존 NNLM의 복잡한 non-linear hidden layer를 제거한 CBOW와 Skip-gram
- output layer 최적화: Hierarchical Softmax, Negative Sampling.
- 벡터 학습: 계산량을 획기적으로 줄여 더 큰 데이터로 더 고퀄리티의 단어 벡터를 학습 
- word vector의 linear regularity 입증: 학습된 벡터 단어 간의 linear regularity 표상하고 있음을 실험으로 증명함

### 6. 나의 생각 및 토론 (My Takeaway & Discussion)
- NLP계 bible 중 하나와 같은 이 논문을 제대로 읽고 이해함에 목적을 두었으며, word2vec의 단어 벡터 학습 과정과 word algebraic operation에 대해 공부할 수 있었다.
- 벡터의 linear regularity를 발견한 것이 매우 흥미롭게 느껴졌다. 언어학적으로만 해석할 수 있으리라 여겨지던 단어간의 문법적, 의미적 관계를 컴퓨터 상에서 vector 연산으로 나타낼 수 있다는 점이 놀라웠으며 나도 언어학적 관계를 컴퓨터 연산에 끌어오는 다양한 방법론을 고안해내는 연구를 하고싶다.