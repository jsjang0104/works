# Literature Reproduction Report 2025.11.13

**Title**: "Efficient Estimation of Word Representations in Vector Space"
**Authors**: [Tomas Mikolov, Kai Chen, Greg Corrado, Jeffrey Dean]
**Journal**: "arXiv:1301.3781"
**year**: 2013


## Experiment Environment Log
Hardware
- CPU: 13th Gen Intel® Core™ i5-1340P
- RAM: 16.0 GB
- GPU: Intel(R) Iris(R) Xe Graphics (not used for learning)

Software 
- OS: Windows 11 Home
- Python: Python 3.10.0
- PyTorch: 2.9.0


## Experiment I (2025.11.10)
### 1. Structure
- dataset size: Leipzig Corpora Collection 2024 English news sentences 10K (https://wortschatz.uni-leipzig.de/en/download/eng)
- minimum count: 3 (original vocabulary size: 23632, filtered vocabulary size: 7066)
- hyperparameter:  
    - embedding dimension: 50
    - window size: 2
    - negative samples: 5
    - batch size: 64
    - epoch: 100
- model: CBOW with negative sampling


### 2. Result
- total training time: 1879.14 sec
- word embedding semantic similarity test (cosine similarity)
    - france vs germany: 0.272
    - man vs woman: 0.451
    - king vs queen: 0.164
    - king vs man: 0.360
    - france vs woman: 0.223
    - king vs france: 0.274


### 3. Discussion
The cosine similarity between 'man' and 'woman' is relatively high (we can assume that they are placed in similar vector space). However, the others are not. (france and germany, king and queen). Moreover, word vector analogy cannot be performed.

- The model may have failed to learn the semantic relationship between remote words, because of the small window size. Man and Woman appear often closely - such as in the expression "a man and a woman..." - but king,queen and france,germany don't appear that often.
- The embedding dimension(50) might be insufficient to express all the semantic, syntactic meaning of a word.
- A minimum count of 3 is likely too low, the model couldn't filter out noisy words.
- The Loss seems small enough. Number of epochs can be decreased.


### 4. Modification
- window size: 2-> 10
- embedding dimension: 50->100
- min_count: 3->5
- epoch: 100->30


## Experiment II (2025.11.10)
### 1. Structure
- dataset size: Leipzig Corpora Collection 2024 English news sentences 10K (https://wortschatz.uni-leipzig.de/en/download/eng)
- minimum count: 5 (original vocabulary size: 23632, filtered vocabulary size: 4443)
- hyperparameter:  
    - embedding dimension: 100
    - window size: 10
    - negative samples: 5
    - batch size: 64
    - epoch: 30
- model: CBOW with negative sampling


### 2. Result
- total training time: 192.74 sec
- word embedding semantic similarity test (cosine similarity)
    - france vs germany: 0.111
    - man vs woman: -0.008
    - king vs queen: 0.044
    - king vs man: -0.016
    - france vs woman: 0.181
    - king vs france: 0.096


### 3. Discussion
The results are even worse than the first experiment. 
- The number of epochs reduction might be the reason.
- The dataset size should be increased.
- Simultaneous modification of multiple hyparparameters made the following experiment hard to analyze why it failed again.


### 4. Modification
- epoch: 30 -> 100
- data set size: 10K -> 30K


## Experiment III (2025.11.10)
### 1. Structure
- dataset size: Leipzig Corpora Collection 2024 English news sentences 30K (https://wortschatz.uni-leipzig.de/en/download/eng)
- minimum count: 5 (original vocabulary size: 42923, filtered vocabulary size: 9346)
- hyperparameter:  
    - embedding dimension: 100
    - window size: 10
    - negative samples: 5
    - batch size: 64
    - epoch: 100
- model: CBOW with negative sampling


### 2. Result
- total training time: 1789.66 sec
- word embedding semantic similarity test (cosine similarity)
    - france vs germany: -0.071
    - man vs woman: 0.241
    - king vs queen: 0.199
    - king vs man: 0.165
    - france vs woman: 0.178
    - king vs france: 0.192


### 3. Discussion
- The results still show a significant degradation compared to Experiment I. 
- From comparison with other researchers' reports, (2025.11.10)
    - The extremely small dataset size might be the primary reason for the failure.
    - Epochs can be drastically decreased (even to a single-digit-number). The original experiment from the paper was 3.
    - A GPU is recommended for more efficient experimentation. However, we consistently used the current H/W environment (CPU only) for experiments I, II, and III. Therefore, GPU usage will be deferred.


### 4. Modification
- data set size: 30K -> 1M
- epoch: 100 -> 3


## Experiment IV (2025.11.12)
### 1. Structure
- dataset size: Leipzig Corpora Collection 2024 English news sentences 1M (https://wortschatz.uni-leipzig.de/en/download/eng)
- minimum count: 5 (original vocabulary size: 291199, filtered vocabulary size: 69043)
- hyperparameter:  
    - embedding dimension: 100
    - window size: 10
    - negative samples: 5
    - batch size: 64
    - epoch: 3
- model: CBOW with negative sampling


### 2. Result
- total training time: 12141.47 sec
- word embedding semantic similarity test (cosine similarity)
    - france vs germany: 0.216
    - man vs woman: 0.533
    - king vs queen: 0.063
    - king vs man: 0.296
    - france vs woman: 0.081
    - king vs france: 0.303


### 3. Discussion
- Analysis
    - only cosine similarity between 'man and woman' is relatively noticable, while others are not.
    - Cosine similarity between 'king and france' is higher than 'france and germany' and 'king and queen'. This implies definite failure of experiment, despite the significant growth in training time.
- Hypothesis for Failure
    - **Limitation of dataset size**: The dataset size where original research of Word2Vec implemented was 100 billion(1000억). This is significantly larger than the current dataset 1 million(100만). 


## Conclusion
1. Summary of Experiments
    - In this paper, to overcome the limitation of dataset size I assumed that compensating for the small dataset by using a large number of epochs in experiment I,II,III would be effective. But this attempt couldn't make noticeable results.
    - Despite similar hyperparameter set-up with original paper in experiment IV, huge difference in dataset size affected the quality of the results.
    - The CBOW architecture, which averages context vectors, may have struggled to capture signals from rare words within our extremely small dataset. This could have contributed to the poor performance, as the original paper notes Skip-gram is often superior for smaller corpora.
2. Future work
    - To make hardware environment equivalant, all experiments were conducted with **CPU**. To perform with larger dataset size, we need to use GPU in future work.
    - When we get noticeable results, **word analogies**, which are one of the most significant results in original paper, can be also experimented. 
    - Rather than using CBOW model, we can try **Skip-gram** to overcome small dataset.