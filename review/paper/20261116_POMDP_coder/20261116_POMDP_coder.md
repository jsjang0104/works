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

## 3. Background

## 4. POMDP Coder

## 5. Experiments

## 6. Discussion

## 7. Limitation