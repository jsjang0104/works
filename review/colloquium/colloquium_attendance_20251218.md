# 제 92회 한국외국어대학교 대학원 영어학과 콜로키움 참석
Generalization in the Era of Artificial General Intelligence (AGI)

한국외국어대학교 Language&AI융합학부 이재홍 교수님


## 발표 내용
### **Generalization의 발전 단계**
- detecting distribution shifts: 학습된 걸 제외하고 좀 더 다양한 feature에 대해 일반화 (노이즈의 영향 줄이기)
- transfer learning
- multi-task learning
- few shot learning
- continual learning
- adversarial learning (적대적 학습)

### **Transfer Learning & Multitask Learning**
1. Transfer Learning
- 기존의 source data로 pretrained model을 fine tuning해서 새로운 domain에서의 성능 발현
- neural network로 학습 (task specific한 layer를 층 뒤에 헤드로 붙여넣음)
- 1 task 1 model

2. Transfer Learning - GPT 1
- 각각의 NLP task에 대하여 fine-tuning (Q&A, summarizing, task classifirer, task prediction 등)
- 이 때 transformer가 나옴. 여기에 decoder 부분만 떼와서 붙임
- general text DB를 사용하여 GPT 1으로 사전학습 후 -> 이후 각 task에 대해 fine-tuning
- input의 구조도 같이 변화를 시킴 -> 모델 구조 변화 없는 zero shot fine tuning 
    - 각각의 여러가지 task에 대한 special token 정의 (to French, summarize 등)
    - 그럼 이런 스페셜 토큰마다 사전에 구축된 방대한 데이터 이용

3. Multitask Learning
- AGI는 multi task learning을 얼마나 잘하냐의 관점으로도 해석 가능 (핵심: 사람의 능력만큼 발현할 수가 있느냐)
- head가 한 번에 여러 개의 task를 처리함
- 여러 task 1 model
- 한계성: multi task 수행 시 성능이 나빠짐 (오히려 제대로 된 한 개도 수행 못함)
    - task interference 서로 간섭
    - 그래서 이걸 어떻게 돌파? -> LLM 기반 **gerative model**로 극복

4. Multi Task Learning - GPT 2
- task 간 간섭 문제 -> few shot learning으로 해결
- 학습을 할 때 example을 같이 보여주는 방식
- 위와 같은 special token 방식 x -> 자연어로만 특정 task 수행 (in-context learning)
- 공학적 지식 없이 채팅으로만 task 수행 가능
- inner loop: task별 처리 능력 / outer loop: gradient update

### **Foundation Model에 관하여**
1. Foundation Model
- 그 전까지는 엄청 판타스틱한 이론, 기술을 연구해 냄으로서 모델 성능 향상을 도모
- 그저 data, model size를 늘리는 것만으로도 성능이 많이 올라감
- 현재까지 정설로 받아들여져 왔음

2. AGI: scale is all you need
- 그런데 이제 슬슬 한계에 부딪히는 중
- 이미 정제가 잘 되어 있는 고급 데이터들은 없어지기 시작
- data를 모델이 받아들이는 학습 알고리즘에서의 한계성도 보임
- 다시 돌아가서 이론, 기술을 해야하는 단계로 진입

### **Continual Learning**
1. Robotics
- 이미 학습해 놓은 데이터로 새로운 환경에 적응하는 방법이 필요함
- 예시 1: 자율주행자동차가 마주할 수 있는 새로운 환경
    - 환경 변화
    - 법제 변화
    - 노후화된 센서로 인한 노이즈 등
- 예시 2: 대화형 인공지능
    - 사용자 마다의 personalize
- robotics의 발전을 위해서는 continual learning이 필요

2. Problem
- Catastrophic Forgetting (치명적 망각)
    - 인지과학에서 온 개념
    - 뉴런들은 강제적으로 뇌속에서 기억을 잊어버리게 하는 매커니즘이 있음
    - 이게 똑같이 continual learning에서도 발현됨
- Transfer Interference and Overgeneralization (전이 간섭, 과잉 일반화)
    - 원어 언어학에서 bilingual들에게 나타나는 현상
    - 이게 똑같이 continual learning에서도 발현됨

3. Solution
- regularization: 새로운 task에 대한 규제. 특정 정보를 학습했을 때 기존 정보가 없으면 intersectional part로 강제로 규제
- experience reply: 경험을 반복. 오답노트에다 적어놓고 참조를 하면서 잊어버리지 않는 개념. Biology에서의 장/단기 기억 문제를 data 관점으로
- architecture: NN을 새로운 task가 올 때마다 확장 (새로 구조를 확장함으로서 task들 간의 간섭을 줄임) -> 단점: 새 task마다 모델을 늘려야됨
- adaptor: 모델의 구조에서 저장할 부분과 빠르게 변할 부분을 구분해서 학습
- mixture of expert: 여러가지 model을 두고 각 task마다 allocate (최근 GPT5가 이것 때문에 구설수에 올랐었음)


### **교수님 연구 내용**
1. 과거 데이터, 새 데이터 간의 간섭을 최소화하면서 pretraining을 지속하는 방법 (2022)
- 교수님이 전세계 최초임 ㄷㄷ
- 지금 LLM들은 대부분 블랙박스 형태로 구성이 되거나 규모가 너무 커서 재학습이 어려움

2. Efficient Continual Adaptation: 실시간으로 바로바로 들어오는 데이터에 대한 연구
- 장기기억, 단기기억을 수학적 모델링
- 교수님 자랑: 맘바보다 빨랐음
- 실시간 들어오는 data들에 대해서 빠른거, 느린거를 분리
- 모델 파라미터 노이즈가 줄어듦
- 이렇게 학습을 하더라도 정말 이상한 데이터가 들어올 때가 있음 -> 모델이 취약해짐
- 이상치 노이즈가 발생할 경우 확률적으로 confidence bound에서 벗어나면 역으로 bound 안으로 들어오게 하는 형태로 input data자체는 조절함 (사람으로 치면 현실 부정)

3. application
- 음성 인식: 실시간으로 들어오는 환경적인 noise들을 줄임 
- 사람 각각에 대한 personalization
- online editing for LLM


### **Getting insights from humanities**
1. "공학적으로 성능이 좋은 모델"과 "사람의 마음을 움직이기 위한 좋은 모델"은 다른 문제임
- 공학적 접근: 모든 것을 숫자로 이야기함
- 인문학적 접근: 사람과 interaction을 할 수 있는 동반자 (반려)로서의 인공지능을 연구하기 위해 필수적

2. 스팀 게임 become human: 기계들이 사람과 유사하게 됐을 때 부딪힐 수 있는 수많은 윤리적, 사회적 문제들을 종합적으로 다루고 있음.
- 규율을 잘 지키는 인공지능 / 노동자인데 혁명을 바라는 인공지능 / 사람의 마음을 돌봐주는 카운셀러로서의 인공지능
- 이 게임에서 실제 AI와 사람들간의 interaction을 엿볼 수 있음
- 최근 GPT3가 사람과의 소통을 위해 사용자 feedback을 수집 중 -> 강화학습을 통해 humanity 학습 (프롬프팅을 통한 humanity 주입)

3. 교수님 생각: AGI(Artificial General Intelligence)가 아닌 **GAI**로 불려야됨 (General Artificial Intelligence)
- 즉 사람다운 AI를 만드는 것이 아닌 **사람을 위한 AI**를 만드는 것이 목적이 되어야

4. 인류의 사고방식은 과거의 것에 근간을 두기 마련
- 자동차가 발명돼도 -> 말은 이동수단으로서의 의미를 유지
- 인쇄술이 발명돼도 -> 필사본은 책으로서의 의미를 유지
- AI가 등장해도 인간 고유의 영역은 사라지지 않을 것

5. 기술적 불안정화 매커니즘    
- 희소성에서 풍요로움의 전환은 기존의 방어 기제(노력, 체계 등)를 무너트림 -> 즉 AI가 주는 풍요로움에 중독되면 안 됨
- 생성형 AI가 무너뜨릴 많은 인간 고유의 가치: 
    - 노력의 증명: 에세이, 입사 절차 등
        - 요즘엔 AI가 다 해줌
        - 그렇다면 다른 방식으로 자기 자신을 어떻게 나타낼 것이냐?
        - '노력의 증명을 만들어내는 매커니즘 자체'를 AI로 만들어야
    - 진위의 증명
    - 정확성의 증명
    - 인간성의 증명: 글의 저작권 등 (어디까지가 사람의 창작의 영역인가?)
- **인간 고유의 가치**를 지키지 위해서는 앞에서 봤던 공학적 방법론 보다는 다른 방법에 대한 고민 필요 (특히 **인문학적 접근**)
    
## 현장 Q&A
1. Q. 할루시네이션을 인공지능의 창의성으로 볼 수 있는지?
- 지금은 할루시네이션을 창의성의 영역으로 보기에는 힘듦
- 더 높은 수준의 data로 AI가 humanities를 포함하게 된다면 그때부터는 창의성이라고 볼 수 있지 않을까
- 그러기 위해서는 공학이 아닌 다른 domain의 연구자분들이 공돌이들이 만들어 낸 data들에 대한 validation mark를 붙여주어야 함 (dataset들에 대한 사람의 인증이 필요)

2. Q. (내 질문) 최근 지피티가 여러 답변을 내놓고 사용자 feedback을 받는 게 reinforcement learning 목적이고 이걸 통해 humanity를 학습한다고 하셨는데, '사용자 입력과 피드백'이 '강화학습에서의 보상개념'이 아니라, 잘 정제된 data로서 'supervised learning의 label 개념'으로서 사용할 수 있는 방법이 현재 존재하는지 궁금합니다. 만약 없다면 그러한 방법이 humanity 학습 연구로서 어떻게 이루어질 수 있을지 교수님의 인사이트를 여쭙고 싶습니다.
- 생각보다 잘 정제된 형태의 data로서 human feedback을 쉽게 얻을 수 없음
- (중간 말씀 내용 타이핑 놓침ㅠㅠ)
- 사람과 비슷한 정답을 얻기 위해서는 사람처럼 동작하는 다른 모델의 정답을 가져와서 학습을 시키는 방법이 있음 (그게 GPT와 딥시크의 방식이라고 소문이 들림. 한마디로 날먹)
- 여기서 나오는 output을 정형화 / structure화 시킬 수 있으면 좋겠지만, 아직은 그런 연구가 없음 

## 들었던 생각
1. 언어학에 관하여
나는 언어학 중 음성학만 좋아하고 다른 분야는 전혀 흥미가 없다. 특히 이번 학기에 인지언어학 과목을 들으면서 정말 하기 싫었는데, 이번 콜로키움 때 교수님께서 인지언어학의 내용 (장기기억/단기기억)을 공학적 모델링 연구로 연결시킨 사례를 말씀해주시니 역으로 인지언어학에 흥미가 생겨버렸다. 이번 학기에 잘 좀 할 걸...하는 후회와 함께. 지식에 대한 편식을 최대한 줄이고, 내가 어떤 걸 배우든간에 나중에 언젠가는 내 연구의 자양분이 될 것이라는 생각으로 재미 없어도 매순간 최선을 다해야겠다고 반성했다.

2. 인문학에 관하여
평소 수업때는 공학 내용으로만으로도 수업 진도 나가시느라 시간이 부족하셔서 AI를 바라보는 인문학적 인사이트에 관한 교수님의 견해를 들을 기회가 없었는데, 이번 기회를 통해 들으니 감회가 남달랐다. 본 전공이 어문학인 학생으로서 평소에 주변 선후배, 동기들이 하는 'AI의 발전으로 먹고살길이 막막하다'는 하소연을 많이 듣고 있다. 사실 이번 교수님의 강의는 그러한 내 주변 사람들에게 들려주고 싶은 강의였다. 그리고 나 또한 항상 한국외대라는 특수한 정체성을 가진 학교의 학생으로서 어떻게 AI 시대의 흐름에 인문학적 가치를 투영시킬 수 있을지에 관한 고민이 많았는데, 그것에 대한 해답을 엿볼 수 있는 강의였다. 물론 엿보기만 하고 진짜 정답은 내가 연구를 통해 헤쳐나가면서 직접 찾아가는 것이라고 생각 중이다.
추가로, 교수님께서 AGI 아니라 GAI를 지향해야 한다고 말씀해주셨는데, 평소에 내가 갖고 있던 입장과 비슷한 맥락을 공유하는 것 같아 신기하기도 하고 감사했다. 내가 혼자 생각하는 거랑, 교수님처럼 한 분야의 정점에 서 계신 분이 해주시는 말이랑은 그 깊이가 다르니까... 내 생각에 힘이 실리는 기분이였다. (물론 내가 이해한 방향이 교수님이 말씀하시고 싶었던 내용과 약간 다를 수는 있겠지만...)
공학을 공부하지 않는 주변인들이 내게 AI에 관한 견해를 물을 때 나는 항상 사냥개에 비유를 하곤 한다. AI는 사냥개고 사냥개를 길들여야 한다, 사냥개가 두려워서 피한다면 사냥개는 당신이 사냥할 짐승들을 대신 먹어치울 것이지만 사냥개에 대해 이해하고 길들인다면 당신에게 몇십 배의 사냥감을 물어다 줄 것이라고... 그리고 나는 사냥개 수의사가 되고 싶다...