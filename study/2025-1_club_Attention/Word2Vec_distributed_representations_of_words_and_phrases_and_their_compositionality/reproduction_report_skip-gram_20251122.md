# Literature Reproduction Report 2025.11.21

- **Title**: "Distributed Representations of Words and Phrases and their Compositionality"
- **Authors**: Tomas Mikolov et al.
- **Journal**: "arXiv:1310.4546"
- **year**: 2013

## 1. 실험 목적
1. 지난번 CBOW 구조의 word2vec model 구현 report에서 유의미한 결과를 찾지 못했음으로, word analogy test와 cosine similarity test에서 실제 논문 실험 결과와 유사한 성능을 내는 것을 목적으로함

2. 지난번 report에서의 최승택 교수님 피드백 반영
  - cosine similarity가 실험의 성공의 척도를 반영하는 건 아님 -> 다른 평가 방식 도입하였음 (word analogy test, cosine similarity test기반 유사 단어 query)
  - training loss 기록 필요 -> 시각화 코드 추가
  - naive whitespace tokenization(예전 방식) 보다 recent tokenizer from LLMs 사용 -> BPE 사용 시도 (Experiment I only)

3. 지난번 report에서의 Attention 학회원들 피드백 반영
  - colab GPU 사용 추천 -> local CPU 사용 고집을 버리고 google colab에서 무료 GPU 사용
  - 실험 시행착오 기록 호평 -> 유지

4. 논문이 제시한 두 가지 쟁점 중 subsampling은 구현하였으나, phrase 학습은 구현하지 않음.

5. 지난번 report에서 사용했던 CBOW가 아닌 Skip-gram 구조를 사용하여 두가지 모델 코드에 대해 차이점을 학습함.

## 2. Experiment Log
### 1. Environment
Hardware & Infrastructure
- Platform: Google Colab (Cloud Computing)
- GPU: NVIDIA Tesla T4 (VRAM 16GB)
- Local Environment (Preprocessing & Control):
  - CPU: 13th Gen Intel® Core™ i5-1340P
  - RAM: 16.0 GB
  - OS: Windows 11 Home

Software & Library
- Language: Python 3.12.12
- Deep Learning Framework: PyTorch 2.2.2
- Libraries: TorchText (Dataset), Transformers (Tokenizer), Matplotlib (Visualization), Numpy

### 2. Dataset *by Gemini*
- Source: AG_NEWS (News Classification Dataset)
- Volume: Total 127,600 Samples (Train: 120,000 / Test: 7,600)
- Characteristics: World, Sports, Business, Sci/Tech의 4가지 주제로 구성된 뉴스 기사 데이터로, 고유명사와 전문 용어가 다수 포함됨.

### 3. 모델 구조 및 특이사항
- **모델**: Skip-gram with negative sampling
- 최적화 방법:
  - Subsampling: Frequent Words의 학습 확률을 낮춤
  - Dynamic Window: 윈도우 크기를 동적으로 조절하여 중심 단어에 가중치 부여 *by Gemini*
- 자꾸 import해둔 게 날아가고, 캐시가 충돌하는 상황이 발생하여서 실험 하나당 하나의 cell 안에 모두 구현하였음. (하나의 실험을 진행할 때 마다 런타임을 모두 초기화)
- 코드 생성 전반에 제미나이의 도움을 받았음 (따로 명시x)
- text 생성 일부에 있어 제미나이의 도움을 받았음 (명시o (*by Gemini*))

## 3. Experiment I

### 3-1. Hyperparameter
- 임베딩 차원 = 100
- window sizse = 5
- 네거티브 샘플링 = 5
- learning rate = 0.003
- 배치 사이즈 = 1024 # batch size
- 에포크 = 5
- minimun frequency = 5

### 3-2. Tokenization
Byte-Pair-Encoding: recent tokenizer from LLM을 사용하기 위해 BPE(GPT-2 Tokenizer) 시도.
- 형태소 분석에 강함.
- 예: apples can be decomposed into apple and -s

### 3-3. Result

1. Training Loss 경향: training loss가 properly하게 decrease하는 중
![image.png](attachment:image.png)

2. Cosine Similarity 계산을 통한 유사 단어 질문😭
- [Query] microsoft
  - Ġmicro: 0.6243
  - Ġauthentication: 0.6126
  - Ġexploit: 0.5390
  - think: 0.5385
  - Ġinnovation: 0.5357

- [Query] football
  - Ġsubstituted: 0.4875
  - Ġscrimmage: 0.4691
  - Ġstale: 0.4601
  - Ġmatch: 0.4356
  - Ġjumping: 0.4349

- [Query] president
  - Ġpresident: 0.5021
  - Ġchoosing: 0.4810
  - idate: 0.4756
  - Ġunrealistic: 0.4480
  - Ġvice: 0.4424

- [Query] war
  - rahim: 0.5435
  - enegger: 0.5222
  - Ġtraitor: 0.4855
  - Ġleftist: 0.4822
  - Ġconvened: 0.4795

3. Word Analogy Test 😭
- [Analogy] man:king = woman:?
  - inic (0.4361)
  - Ġdonation (0.4071)
  - Ġlifetime (0.4040)

- [Analogy] bush:president = jobs:?
  - direction (0.4057)
  - Ġreorgan (0.4042)
  - Ġpayment (0.3920)

### 3-4. Discussion
1. **결과 출력 형태가 이상함**: BPE를 통해 처리한 Token의 형태가 그대로 출력 (공백 표현 Ġ 등). 이를 다시 사람이 알아볼 수 있는 형태로 바꿔주는 코드의 부재 때문임

2. **단어가 아닌 형태소적/철자적 파편 형태 출력**: 이는 얕은 신경망 구조를 갖고 있는 Word2Vec 모델 구조상, 쪼개진 서브워드(Subword) 벡터들을 문맥적으로 다시 결합(Re-composition)하여 하나의 의미로 통합하는 Attention 메커니즘이 부재하기 때문 *by Gemini*

3. **Evaluation 결과가 유의미하지 않음**: 2번과 같은 원인에서 기인한 것으로 보임.

1,2,3로부터 Tokenization기법을 BPE에서 **Basic English Tokenizer**로 변경 (Naive White Space보다 더 정확: 소문자화 + 구두점(, . ! 등)을 단어에서 떼어냄)

4. GPU 사용으로 학습시간이 예상보다 많이 짧아 좀 더 나은 품질을 위하여 **hyperparameter 조정**
- window size: 5 -> 10
- epoch: 5 -> 15
- minimun frequency: 5 -> 10

## 4. Experiment II
### 4-1. Hyperparameter
- 임베딩 차원 = 100
- window sizse = 10
- 네거티브 샘플링 = 5
- learning rate = 0.003
- 배치 사이즈 = 1024 # batch size
- 에포크 = 15
- minimun frequency = 10

### 4-2. Tokenization
Basic English Tokenizer: Normalization (소문자화) -> Punctuation Splitting (구두점 분리)
- 단어 단위 토큰화
- 예: Hi! -> hi

### 4-3. Result
1. Training Loss 경향: training loss가 properly하게 decrease하는 중
![image.png](attachment:image.png)

2. Cosine Similarity 계산을 통한 유사 단어 질문
- [Query] microsoft 😄
  - software: 0.6035
  - server: 0.5773
  - msft: 0.5548
  - vulnerabilities: 0.5541
  - pack: 0.5462

- [Query] football 😄
  - chester: 0.5503
  - coach: 0.5412
  - smith: 0.5352
  - micky: 0.5026
  - players: 0.4976

- [Query] president 😄
  - vice: 0.5408
  - bush: 0.5064
  - ally: 0.5041
  - emphasize: 0.4924
  - elected: 0.4857

- [Query] war 😄
  - sarajevo: 0.4962
  - favoring: 0.4874
  - envoy: 0.4837
  - yugoslavia: 0.4811
  - sudans: 0.4630

3. Word Analogy Test
- [Analogy] man:king = woman:? 😭
  - dancer (0.5620)
  - norodom (0.5264)
  - cambodian (0.5080)

- [Analogy] bush:president = jobs:? 😭
  - bombardier (0.4913)
  - investor (0.4418)
  - workforce (0.4352)

### 4-4. Discussion
1. Word Analogy의 실패: **데이터셋 편향** *by Gemini*
- [Analogy] bush : president = jobs : ? 에서 apple, ceo를 기대했지만 모델 예측은 workforce, investor임
  - AG_NEWS 뉴스 데이터는 2004년 자료이고 당시 "Jobs"는 스티브 잡스보다 "일자리(Employment/Economy)"라는 의미로 훨씬 많이 쓰였음.
  - 해석: bush가 president으로서 정책을 다루듯, jobs(일자리)는 노동력(workforce)이나 경제와 관련이 있다는 문맥을 학습.

- [Analogy] man : king = woman : ? 에서 queen을 기대했지만 모델 예측은 norodom (노로돔 시아누크 캄보디아 국왕(?))임
  - 뉴스 데이터 특성상 "옛날 이야기 속의 King"보다는 "실존 인물 캄보디아 국왕 노로돔"에 대한 기사가 많음
  - 해석: King이라는 단어의 벡터가 '남성 통치자'라는 추상적 개념보다는 '노로돔'이라는 고유명사 옆에 형성됨

2. Cosine Similarity 기반 Query의 성공
- Cosine Similarity는 벡터 공간 내 유사한 부분에 뭉쳐있는 것에 대한 측정이기 때문에 정교한 연산이 필요 없음 (Microsoft - Software 등 우수한 evaluation 품질을 보임)
- Analogy는 벡터 공간 내에서 정교한 평행사변형을 그려야 하므로 논문 수준으로 학습이 훨씬 많이 이루어져야함

3. **Learning Rate Scheduler** 추가: 학습 후반부에 학습률을 줄여줘야 더 정교한 벡터 공간 생성 가능 *by Gemini*
- 높은 학습률을 고정해서 유지할 경우, 학습 후반부에 Global Minimum 근처에 도달하더라도 수렴하지 못하고 주변을 맴도는 Oscillation 현상이 발생할 수 있음
- 대신 초반 learning rate를 크게 수정 0.003 -> 0.025

## 5. Experiment III
### 5-1. Hyperparameter
- 임베딩 차원 = 100
- window sizse = 10
- 네거티브 샘플링 = 5
- learning rate = 0.025
- 배치 사이즈 = 1024 # batch size
- 에포크 = 15
- minimun frequency = 10

### 5-2. Tokenization
Basic English Tokenizer: Normalization (소문자화) -> Punctuation Splitting (구두점 분리)
- 단어 단위 토큰화
- 예: Hi! -> hi

### 5-3. Result
1. Training Loss 경향:

- 초기 오버슈팅: Epoch 0에서 1로 넘어가는 시점에 Loss가 오버슈팅이 발생함. 이는 Adam Optimizer의 관성(Momentum)과 초기 높은 학습률(High Learning Rate)로 인해 최적점 탐색 과정에서 발생한 일시적인 현상으로 분석됨. *by Gemini*
- 안정적 수렴 (Stable Convergence): Epoch 2 이후부터는 부드럽게 감소함.

최종 검증을 위하여 Experiment III에서만 추가 실험을 진행하였음

2. Cosine Similarity 계산을 통한 유사 단어 질문
[Query] medal 😄
  - meters: 0.6535
  - athens: 0.6438
  - freestyle: 0.6392
  - olympic: 0.6389
  - phelps: 0.5901

[Query] cpu 😄
  - xserve: 0.4809
  - usability: 0.4641
  - cordless: 0.4418
  - gran: 0.4365
  - 4-gigahertz: 0.4345

[Query] gold 😄
  - olympic: 0.5785
  - olympics: 0.5728
  - medal: 0.5696
  - silver: 0.5624
  - phelps: 0.5467

[Query] internet 😄
  - users: 0.6179
  - customers: 0.5760
  - web: 0.5671
  - search: 0.5439
  - computer: 0.5437

[Query] microsoft 😄
  - xp: 0.6307
  - windows: 0.6283
  - software: 0.6008
  - users: 0.5970
  - designed: 0.5897

[Query] football 😄
  - coach: 0.5445
  - soccer: 0.5405
  - dolphins: 0.5392
  - club: 0.5307
  - henry: 0.5293

[Query] president 😄
  - minister: 0.6303
  - coalition: 0.6108
  - bush: 0.6104
  - democratic: 0.6063
  - elections: 0.6034

[Query] war 😄
  - hiding: 0.5535
  - afp: 0.5350
  - iraq: 0.5182
  - genocide: 0.5142
  - abuses: 0.5010

3. Word Analogy Test
[Analogy] china:beijing = japan:? 😶
  - korea (0.4301)
  - iran (0.4273)
  - chinese (0.4263)

[Analogy] france:paris = germany:? 😶
  - balance (0.4186)
  - struggled (0.4010)
  - reuters (0.3945)

[Analogy] microsoft:software = intel:? 😄
  - devices (0.5559)
  - processors (0.5432)
  - dual-core (0.5343)

[Analogy] microsoft:windows = google:? 😄
  - search (0.5490)
  - beta (0.5095)
  - web (0.5031)

[Analogy] swimming:phelps = cycling:? 😶
  - gymnastics (0.4573)
  - silver (0.4239)
  - spain (0.4088)


### 5-4. Discussion
1. Cosine Similarity 계산을 통한 유사 단어 질문: 모든 Query에서 좋은 결과를 나타냄. Word Vector Space가 잘 형성되었음을 알 수 있음

2. Word Analogy Test
- 성공 사례: "기업"과 "핵심 비즈니스"간의 관계를 완벽하게 계산해냄!!!
  - [Analogy] microsoft:software = intel:devices
  - [Analogy] microsoft:windows = google:search
- 실패 사례
  - [Analogy] china:beijing = japan:korea 뉴스 데이터 특성상 '국가-수도'의 지리적 사실보다 동북아 외교 관계(중국-일본-한국)의 언급 빈도가 압도적으로 높아, 모델이 일본의 연관 단어로 수도(도쿄)가 아닌 외교적 파트너(한국)를 선택함 *by Gemini*
  - [Analogy] france:paris = germany:balance 독일과 프랑스가 주로 경제/정치 뉴스에서 함께 다루어지며 '무역 수지(Trade Balance)'나 '세력 균형(Balance of Power)' 같은 경제·시사 용어와 강하게 연결되어 벡터가 형성되었기 때문임 *by Gemini*
  - [Analogy] swimming:phelps = cycling:gymnastics 수영, 사이클, 체조가 모두 '하계 올림픽 인기 종목'이라는 좁고 밀집된 클러스터를 형성하고 있어, 벡터 연산 결과가 특정 선수를 가리키지 못하고 가장 가까운 다른 인기 종목(체조)으로 편향됨 *by Gemini*

## 6. Conclusion
1. Skip-gram과 같은 얕은 신경망 구조에서는 BPE 방식보다 word 기반의 tokenization 기법이 더 잘 작동함

2. adaptive learining rate 도입의 중요성: global minimum에 가까워질 수록 learning rate를 적게 조정해야 진동현상을 피하고 좀 더 퀄리티 높은 벡터 공간을 만들어 냄

3. Dataset의 bias에 기반한 evaluation을 진행해야 의미있는 결론을 도출해 낼 수 있음

3. 한계 및 발전 방향: 본 실험에서는 원본 논문에서 도출해냈던 중요한 의의중 하나인 multi-word expression이나 phrase 학습을 진행하지 못하였음. 원본에서는 통계적 기법(Unigram/Bigram Counts)을 활용한 전처리 단계에서 Phrases를 식별하였음. 추후 이를 도입하여 재실험해볼 수 있음.