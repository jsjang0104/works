# Public Service Mediation Agent Workflow

한국어: 공공서비스 중재 에이전트 워크플로우

## Context

Hackathon theme: build an AI agent workflow for an industry context in Southeast Asia.

해커톤 주제: 동남아시아의 산업 환경에서 사용할 수 있는 AI 에이전트 워크플로우 제작

Selected topic:

> 특정 국가 안에서 쓰이는 소수언어, 방언, 관료적 행정 용어를 이해하고, 사용자가 공공서비스를 이용할 수 있도록 안내하는 공공서비스 챗봇 에이전트.

Selected country:
> Vietnam

핵심 가정: 많은 공공서비스 RAG 시스템은 사용자가 공식 문서와 같은 언어와 용어로 질문할 수 있다고 전제합니다. 하지만 실제 베트남 국가 내의 agent 사용자는 소수언어, 방언이 섞인 표현, 비공식 베트남어, 오타가 있는 베트남어, 또는 행정 용어가 아닌 생활 언어로 질문할 수 있습니다.

우리의 에이전트는 RAG 앞뒤의 간극에 집중합니다. 사용자의 생활 언어 질문을 표준 베트남어 query로 바꾸고, 제공된 RAG 시스템으로 공식 문서에서 근거 있는 정보를 검색한 뒤, 문서 기반 답변을 사용자가 이해할 수 있는 안내로 다시 바꿔 제공합니다.


## Main Design Decision

별도의 BM25 검색 엔진은 구현하지 않는다.

해커톤의 workflow platform에서는 이미 AI API, 문서 기반 fine-tuning, 주어진 문서에 대한 RAG를 제공한다. 따라서 우리의 기술적 기여는 또 다른 검색 백엔드를 만드는 것이 아니라, 제공된 RAG를 더 잘 활용하게 만드는 에이전트 워크플로우가 되어야 한다.


## Target User Scenario

베트남의 소수언어 또는 방언 사용자가 출생신고, 가구 등록, 건강보험, 복지 지원, 노동허가, 거주 관련 절차 같은 공공서비스에 대해 질문하고 싶어 하는 상황을 가정한다.

사용자는 공식 베트남어 행정 용어를 모를 수 있다. 대신 자신의 상황을 생활 언어로 설명할 가능성이 높다.

Example:


```text
My child was born recently. Where do I report this, and what papers do I need?
```

'출생신고'라는 공식 행정 용어 대신, "아이가 최근에 태어났는데 어디에 신고해야 하고 어떤 서류가 필요한가요?"라는 식의 질문이다. 에이전트는 이러한 질문을 공식 베트남어 공공서비스 검색어로 변환해야 한다.

```text
thủ tục đăng ký khai sinh cho trẻ em
giấy tờ cần nộp khi đăng ký khai sinh
thời hạn đăng ký khai sinh
```

위 표현은 각각 '아동 출생신고 절차', '출생신고 시 제출 서류', '출생신고 기한'처럼 공식 문서에서 검색 가능성이 높은 행정 표현이다.

## Recommended Scope (준기 확인 필요)

해커톤 데모에서는 여러 언어와 여러 도메인을 넓게 지원하기보다, 하나의 좁은 시나리오를 안정적으로 지원하는 것이 좋다.

추천 MVP는 하나의 소수언어 또는 방언 사용자 집단을 정하며, 출생신고나 건강보험 같은 하나의 공공서비스 도메인을 선택하고, 소수언어 핵심 용어와 쉬운 베트남어 fallback을 함께 사용하는 방식이다.

이때 베트남의 모든 소수언어를 넓게 지원한다고 주장하지 않는 것이 좋다. 더 강한 메시지는 작지만 신뢰할 수 있는 중재 워크플로우를 만들고, 이후 확장 가능하다고 보여주는 것이다.

## Team Roles

팀은 전문성에 따라 역할을 나눈다. 

### 홍준기
언어 및 산업 담당은 베트남 맥락, 공공서비스 도메인 지식, glossary, 데모 시나리오, 평가 예시를 맡는다.

### 장지수
엔지니어링 담당은 에이전트 워크플로우 구현, 프롬프트, RAG 연동, UI 또는 데모 스크립트, 평가 실행기를 맡는다.

두 역할은 모두 핵심적이다. 프로젝트는 엔지니어링 워크플로우에 의존하지만, 언어와 공공서비스에 대한 가정이 현실적이지 않으면 워크플로우 자체가 설득력을 잃는다.

## Language and Industry Lead Responsibilities (준기 확인 필요)

언어 및 산업 담당은 데모의 현실성을 책임진다. 이 역할은 단순한 "번역"이 아니다. 베트남 공공서비스 맥락, 사용자 시나리오, 도메인 용어, 최종 에이전트 행동이 실제 사용자에게 말이 되는지를 담당한다.

### 1. Choose the Demo Scope

MVP에서 다룰 좁은 공공서비스 시나리오를 결정한다. 추천 후보는 출생신고, 건강보험 카드, 가구 또는 거주 등록, 복지 지원, 노동 관련 공공서비스다.

선택 기준은 공식 공공서비스 문서가 충분히 있고, 절차가 명확하며, glossary로 만들 가치가 있는 용어가 있고, 심사위원에게 설명하기 쉬우며, 생활 언어와 공식 용어 사이의 간극을 보여줄 수 있는지다.

```text
Chosen demo domain:
Target user:
User problem:
Why this is difficult without mediation:
Expected public-service outcome:
```

선택한 데모 도메인, 대상 사용자, 사용자 문제, 중재 없이는 왜 어려운지, 기대되는 공공서비스 결과를 정리한다.

### 2. Define the Target User Persona

데모를 위한 구체적인 사용자 페르소나를 만든다. 페르소나는 사용자가 누구인지, 어떤 언어 또는 방언 문제를 갖고 있는지, 어떤 공공서비스가 필요한지, 어떤 공식 용어를 모르는지, 어떤 답변이 도움이 되는지를 설명해야 한다.

Example:

```text
Persona:
A parent living in a rural province who speaks limited standard Vietnamese and wants to register a newborn child. The parent does not know that the official term is "đăng ký khai sinh" and asks using everyday language.
```

표준 베트남어 사용이 제한적인 농촌 지역 부모가 신생아 출생신고를 하고 싶어 한다. 이 부모는 공식 용어가 "đăng ký khai sinh"라는 것을 모르고 생활 언어로 질문한다.

이 페르소나는 엔지니어링 담당이 프롬프트와 출력 형식을 설계하는 데 도움을 준다.

### 3. Build the Public-Service Glossary

선택한 도메인에 대해 작지만 품질 높은 glossary를 만든다. glossary는 사용자 질문, 공식 공공서비스 문서, RAG 검색 질의, 최종 답변에 자주 등장할 가능성이 높은 용어에 집중해야 한다.

해커톤에서는 선택한 도메인에 대해 20-50개 정도의 용어를 추천한다.

Recommended fields:

```json
{
  "source_term": "informal, dialect, minority-language, or user-facing term",
  "standard_vietnamese": "official Vietnamese administrative term",
  "english_or_korean_meaning": "brief explanation",
  "domain": "civil_registration",
  "aliases": ["alternate expression", "misspelling", "related phrase"],
  "usage_note": "when this term should be used",
  "example_user_question": "example question using this term"
}
```
`source_term`에는 비공식 표현, 방언, 소수언어 표현, 사용자 친화적 표현을 넣고, `standard_vietnamese`에는 공식 베트남어 행정 용어를 넣는다. 나머지 필드는 의미 설명, 도메인, 별칭, 사용 맥락, 예시 질문을 담는다.

glossary는 크기보다 품질이 중요하다. 현실적인 용어로 구성된 작은 glossary가 인위적으로 큰 glossary보다 낫다.

### 4. Collect Official Terminology

공공서비스 문서에서 사용되는 공식 베트남어 용어를 식별한다.

Examples for birth registration:

한국어: 출생신고 도메인 예시:

- đăng ký khai sinh
- giấy khai sinh
- giấy chứng sinh
- ủy ban nhân dân cấp xã
- người đi đăng ký khai sinh
- thời hạn đăng ký khai sinh
- lệ phí
- hồ sơ
- thủ tục hành chính

위 용어들은 출생신고, 출생증명서, 출생확인서, commune-level People's Committee, 출생신고자, 출생신고 기한, 수수료, 신청 서류, 행정 절차 등을 의미한다.

언어 및 산업 담당은 어떤 용어가 공식 용어인지, 어떤 용어가 사용자 친화적인지, 어떤 용어가 비전문가에게 혼란스러운지, 어떤 용어를 최종 답변에서 설명해야 하는지 검증해야 한다.

### 5. Create Realistic User Queries

데모와 평가에 사용할 사용자 질문 5-10개를 작성한다. 각 질문에는 원래 사용자 표현, 기대되는 공식 베트남어 질의, 기대되는 공공서비스 intent, 핵심 용어, 답변에 포함되어야 할 요소가 들어가야 한다.

Example format:

```json
{
  "user_query": "My baby was just born. Where do I report this?",
  "intent": "birth_registration",
  "expected_official_query": "thủ tục đăng ký khai sinh cho trẻ em",
  "expected_key_terms": [
    "đăng ký khai sinh",
    "giấy khai sinh",
    "ủy ban nhân dân cấp xã"
  ],
  "expected_answer_should_include": [
    "where to apply",
    "required documents",
    "deadline",
    "source document"
  ]
}
```

이 형식은 사용자의 자연스러운 질문이 어떤 공식 질의로 바뀌어야 하는지, 어떤 핵심 용어와 답변 요소가 포함되어야 하는지를 명확히 한다.

한국어: 이 예시는 프롬프트 테스트와 최종 발표에도 유용하다.

### 6. Validate Query Rewriting

에이전트가 생성한 베트남어 질의를 검토한다. 의도가 보존되었는지, 공식 용어가 맞는지, 베트남어로 자연스러운지, 공공서비스 문서 검색에 적합한지, 근거 없는 가정을 추가하지 않았는지 확인한다.

엔지니어링 담당이 생성 과정을 자동화할 수 있지만, 그 질의가 실제로 쓸 만한지는 언어 및 산업 담당이 판단해야 한다.

### 7. Validate Final Answers

최종 공공서비스 답변을 베트남어 명확성, 행정적 정확성, 출처 기반성, 사용자 접근성, 공식 용어 설명의 적절성 관점에서 검토한다.

중요한 구분이 있다. 답변은 유창하지만 행정적으로 틀릴 수 있고, 근거는 있지만 대상 사용자에게 너무 관료적으로 느껴질 수도 있다.

언어 및 산업 담당은 이 두 기준의 균형을 맞추는 역할을 한다.

### 8. Prepare Presentation Context

왜 이 문제가 베트남에서 중요한지에 대한 발표 스토리를 담당한다. 공공서비스 문서는 공식 행정 베트남어를 사용하고, 사용자는 생활 언어로 필요를 설명할 수 있으며, 소수언어 또는 방언 사용자는 추가적인 접근 장벽을 겪을 수 있다. RAG는 입력이 이미 공식 문서 언어와 비슷할 때 잘 작동하므로, 에이전트가 이 간극을 연결한다.

Suggested pitch:

```text
문제는 단순 번역이 아니다. 이것은 공공서비스 중재 문제다. 시민은 삶의 사건을 설명하지만, 정부 문서는 행정 절차를 설명한다. 우리의 에이전트는 그 둘 사이를 매핑한다.
```

### 9. Support Evaluation

성공 기준을 정의하는 데 기여한다. 재작성된 질의가 올바른 공식 용어를 포함하는지, RAG가 기대한 공공서비스 문서를 검색하는지, 최종 답변에 필요한 단계가 포함되는지, 어려운 용어가 설명되는지, 답변이 근거 없는 법적 또는 행정적 주장을 피하는지 확인한다.

언어 및 산업 담당은 작은 평가 세트에 대해 수동 정답 라벨을 제공할 수 있다.

### 10. Hackathon Day Collaboration

구현 중에는 엔지니어링 담당이 파이프라인을 만드는 동안 glossary 용어를 제공하고, 생성된 베트남어 질의를 테스트하며, 부자연스럽거나 오해를 부르는 표현을 수정하고, 가장 좋은 데모 예시를 고르며, 발표 전 최종 출력을 검토한다.

한국어: 발표 중에는 베트남 공공서비스 맥락, 선택한 도메인의 중요성, glossary와 언어 중재 전략, 사용자 질의 재작성의 전후 예시를 설명하고, 언어와 도메인 현실성에 대한 심사위원 질문에 답하는 역할을 한다.

## Engineering Lead Responsibilities

엔지니어링 담당은 실제로 작동하는 시스템을 책임진다.

주요 책임은 에이전트 워크플로우 구현, 제공 RAG 시스템 연동, 프롬프트 템플릿 작성, glossary 로딩 및 활용, 구조화된 중간 출력 생성, 근거 기반 답변 생성, 데모 UI 또는 커맨드라인 데모 구축, 작은 평가 실행, 발표용 기술 설명 준비다.

한국어: 엔지니어링 담당은 fine-tuning 없이도 시스템이 작동하도록 만들어야 한다. Fine-tuning과 ColBERT 스타일 확장은 선택 사항으로 남겨둔다.

## Agent Workflow

```text
User Query
  -> Language / Dialect / Domain Router
  -> Glossary Normalizer
  -> Official Vietnamese Query Generator
  -> Query Expansion Agent
  -> Provided RAG
  -> Grounded Public-Service Answer Composer
  -> Plain-Language / Minority-Language Response Generator
  -> Safety and Escalation Check
```

전체 워크플로우는 사용자 질문을 받아 언어/방언/도메인을 라우팅하고, glossary로 정규화한 뒤, 공식 베트남어 질의를 만들고, query expansion을 수행하고, 제공 RAG를 호출하고, 근거 기반 공공서비스 답변을 만들고, 쉬운 언어 또는 소수언어 보조 표현으로 답변한 뒤, 안전성과 escalation 여부를 점검하는 구조다.

## Step 1: User Query
입력에는 소수언어 용어, 방언 표현, 비공식 베트남어, 오타, code-mixed text, 또는 공공서비스 필요를 비공식적으로 설명한 문장이 포함될 수 있다.
입력은 공식 공공서비스 질의처럼 보일 필요가 없다.

## Step 2: Language / Dialect / Domain Router

목적은 사용된 언어 또는 방언 후보를 감지하고, 공공서비스 도메인을 분류하고, 긴급도나 위험도를 판단하고, 해당 질문이 공공문서 기반으로 답변 가능한지 결정하는 것이다.

가능한 도메인은 시민 등록, 건강보험, 사회복지, 노동 및 고용, 교육, 이민 또는 거주 관련 서비스다.

Output:

```json
{
  "language_hint": "minority_language_or_mixed_vietnamese",
  "domain": "civil_registration",
  "intent": "birth_registration",
  "risk_level": "normal",
  "needs_clarification": false
}
```
이 출력은 언어 힌트, 도메인, intent, 위험도, 추가 질문 필요 여부를 구조화한다.

## Step 3: Glossary Normalizer

목적은 사용자 표현을 표준 베트남어 행정 용어로 매핑하는 것이다.

이 단계는 프로젝트의 주요 차별점 중 하나다. glossary는 언어 전체를 포괄하려고 하면 안 된다. 가치가 높은 공공서비스 용어에 집중해야 한다.

Recommended glossary fields:

```json
{
  "source_term": "everyday_or_minority_language_term",
  "standard_vietnamese": "official Vietnamese term",
  "english_or_korean_meaning": "brief explanation",
  "domain": "civil_registration",
  "aliases": ["informal expression", "misspelling", "dialect variant"],
  "confidence": 0.9,
  "example": "example sentence using the term"
}
```
이 구조는 사용자 표현, 공식 베트남어 용어, 간단한 의미 설명, 도메인, 별칭, 신뢰도, 예문을 포함한다.
포함할 만한 용어 예시는 출생신고, 가구 등록, 건강보험 카드, commune-level People's Committee, 필요 서류, 신청 기한, 수수료, 자격 요건, 예약 등이다.

## Step 4: Official Vietnamese Query Generator

목적은 공식 공공서비스 문서에서 잘 검색될 가능성이 높은 표준 베트남어 질의 하나 또는 여러 개를 생성하는 것이다.

입력에는 원래 사용자 질문, 감지된 도메인, 정규화된 glossary 용어, 사용자 상황이 포함된다.

Output:

```json
{
  "official_query": "thủ tục đăng ký khai sinh cho trẻ em",
  "supporting_queries": [
    "giấy tờ cần nộp khi đăng ký khai sinh",
    "thời hạn đăng ký khai sinh",
    "cơ quan có thẩm quyền đăng ký khai sinh"
  ],
  "key_terms": [
    "đăng ký khai sinh",
    "giấy khai sinh",
    "ủy ban nhân dân cấp xã"
  ]
}
```
이 출력은 대표 공식 질의, 보조 질의, 핵심 행정 용어를 포함한다.

## Step 5: Query Expansion Agent

목적은 제공된 RAG 시스템을 대체하지 않고, RAG에 들어가는 입력의 품질을 높이는 것이다.
이 단계는 PRF로 설명하기보다 `Glossary-Guided Intent-Slot Query Expansion`으로 설명하는 것이 더 적합하다.
PRF는 보통 초기 검색 결과를 보고 쿼리를 다시 확장하는 방식이므로, 해커톤 플랫폼의 제공 RAG 내부를 직접 제어할 수 없을 경우 애매해질 수 있다.
반면 glossary와 intent-slot 기반 확장은 우리가 직접 설계할 수 있고, 공공서비스 중재라는 문제 정의와도 더 잘 맞는다.

확장에 사용할 수 있는 재료는 glossary 용어, 공식 베트남어 별칭, 도메인별 행정 용어, 사용자 intent, 누락된 하위 질문, 그리고 사용자의 상황에서 필요한 공공서비스 slot이다.

### Glossary-Guided Query Expansion

사용자 표현을 glossary를 통해 공식 베트남어 행정 용어와 관련 용어로 확장한다.

예를 들어 사용자가 "아이 태어난 거 신고"처럼 말하면, glossary를 통해 다음과 같은 용어를 연결한다.

```text
사용자 표현:
아이 태어난 거 신고

공식 용어:
đăng ký khai sinh

확장 용어:
- giấy khai sinh
- giấy chứng sinh
- hồ sơ đăng ký khai sinh
- ủy ban nhân dân cấp xã
- thời hạn đăng ký khai sinh
```

이 방식은 검색 모델을 새로 만드는 것이 아니라, RAG가 이해하기 좋은 행정 용어를 입력에 추가하는 방식이다.

### Intent-Slot Query Expansion

공공서비스 질문을 intent와 slot으로 분해한 뒤, slot별 검색 질의를 생성한다.

예를 들어 "아이가 태어났는데 어디에 신고하고 뭐 챙겨가야 해?"라는 질문에는 여러 하위 의도가 섞여 있다.

```text
어디서 해? -> 신청 기관
뭐 필요해? -> 필요 서류
언제까지 해? -> 기한
돈 내? -> 수수료
누가 할 수 있어? -> 자격/대상자
```

이를 구조화하면 다음과 같다.

```json
{
  "intent": "birth_registration",
  "slots_needed": [
    "procedure",
    "required_documents",
    "where_to_apply",
    "deadline"
  ]
}
```

이 slot을 바탕으로 RAG 검색용 질의를 생성한다.

```text
thủ tục đăng ký khai sinh cho trẻ em
hồ sơ đăng ký khai sinh gồm những giấy tờ gì
đăng ký khai sinh ở đâu
thời hạn đăng ký khai sinh cho trẻ em
```

### Multi-Query Generation

Multi-query generation은 LLM API를 사용해 하나의 사용자 질문을 여러 개의 공식 베트남어 검색 질의로 다시 쓰는 방식이다.

단, LLM에게 단순히 "여러 개 만들어줘"라고 요청하기보다, 위에서 추출한 intent와 slot을 바탕으로 통제된 질의를 생성하게 해야 한다.

추천 출력 형식:

```json
{
  "intent": "birth_registration",
  "slots_needed": [
    "procedure",
    "required_documents",
    "where_to_apply",
    "deadline"
  ],
  "queries": [
    "thủ tục đăng ký khai sinh cho trẻ em",
    "hồ sơ đăng ký khai sinh gồm những giấy tờ gì",
    "đăng ký khai sinh ở đâu",
    "thời hạn đăng ký khai sinh cho trẻ em"
  ]
}
```

해커톤 플랫폼 RAG가 여러 query 호출을 허용하면 각 query를 따로 넣고 결과를 merge/deduplicate한다.
여러 query 호출을 허용하지 않으면, 여러 query를 하나의 expanded query로 합쳐서 넣는다.

```text
thủ tục đăng ký khai sinh cho trẻ em; hồ sơ đăng ký khai sinh; giấy tờ cần nộp; cơ quan có thẩm quyền; thời hạn đăng ký khai sinh
```

발표에서는 이 단계를 `LLM-based multi-query generation`이라고 부르기보다 `Intent-Slot Query Expansion`이라고 설명하는 것이 더 좋다.
이렇게 설명하면 "왜 이 query들이 생겼는지"가 명확하고, 평가도 쉬워진다.

Example:

```text
Original normalized query:
đăng ký khai sinh

Expanded query:
thủ tục đăng ký khai sinh cho trẻ em, giấy tờ cần nộp, cơ quan thực hiện, ủy ban nhân dân cấp xã, thời hạn đăng ký khai sinh, lệ phí
```

정규화된 짧은 질의인 "đăng ký khai sinh"를 절차, 필요 서류, 담당 기관, 기한, 수수료 등 공식 문서에서 중요한 검색어가 포함된 질의로 확장한다.

핵심은 새로운 검색 엔진을 만들었다고 주장하지 않는 것이다. 제공된 RAG 시스템에 들어가는 질의 품질을 개선한다고 주장해야 한다.

추천 최종 표현:

```text
Original user query
-> glossary-based term normalization
-> public-service intent classification
-> intent-slot extraction
-> official Vietnamese multi-query generation
-> provided RAG
```

## Step 6: Provided RAG

해커톤에서 제공하는 공공서비스 문서 기반 RAG 시스템을 사용한다.

예상 입력은 공식 베트남어 질의, 확장된 질의, 지원되는 경우 도메인 필터, 지원되는 경우 top-k 설정이다.

예상 출력은 검색된 문서 chunk, 출처 제목, 출처 URL 또는 문서 ID, 가능하다면 confidence score다.

에이전트는 RAG 출력을 근거 자료로 취급해야 한다. 검색된 문서로 답변을 뒷받침할 수 없다면, 사용 가능한 문서에서 해당 답을 확인할 수 없다고 말해야 한다.

## Step 7: Grounded Public-Service Answer Composer

목적은 검색된 공공서비스 문서를 구조화된 답변으로 바꾸는 것이다.

Recommended answer structure:

한국어: 추천 답변 구조:

```text
1. Short answer
2. Who is eligible
3. Required documents
4. Where to apply
5. Deadline or processing time
6. Fee, if mentioned
7. Important cautions
8. Source documents
```

짧은 답변, 대상자, 필요 서류, 신청 장소, 기한 또는 처리 기간, 수수료, 주의사항, 출처 문서를 포함하는 구조가 좋다.

규칙은 검색된 문서만 사실 근거로 사용하고, 출처를 인용하며, 확인된 정보와 불확실한 정보를 분리하고, 법률 또는 의료 관련 과도한 단정을 피하며, 사용자 상황이 부족하면 추가 질문을 하는 것이다.

## Step 8: Plain-Language / Minority-Language Response Generator

목적은 사용자가 답변을 이해할 수 있도록 만드는 것이다.

소수언어 기계번역은 신뢰하기 어려울 수 있으므로, 쉬운 베트남어 설명, glossary에서 가져온 핵심 소수언어 또는 방언 용어, 괄호 안의 공식 베트남어 용어, 단계별 체크리스트를 함께 사용하는 안전한 전략을 쓴다.

시스템이 보장할 수 없다면 완전한 소수언어 번역이 신뢰 가능하다고 가장하지 않는다.

Suggested format:

```text
Simple explanation:
You need to register the child's birth at the commune-level People's Committee.

Official term:
đăng ký khai sinh

What to prepare:
- birth confirmation document
- parents' identification documents
- household or residence information, if required

Source:
- retrieved public-service document title
```

쉬운 설명, 공식 용어, 준비할 것, 출처를 분리해서 보여주는 형식이다.

## Step 9: Safety and Escalation Check

일부 공공서비스 도메인은 위험도가 높다. 예를 들어 이민 또는 거주 자격, 법적 처벌, 의료 자격, 복지 자격, 긴급 서비스가 이에 해당한다.

고위험 답변에서는 문서 기반 안내만 제공하고, 관련 기관에 문의하도록 권장하며, 출처 링크나 기관명을 포함하고, 단정적인 법적 판단은 피해야 한다.

Fallback answer:

한국어: fallback 답변:

```text
I found related public-service information, but I cannot confirm the exact answer from the available documents. Please contact the relevant public office, and bring the following documents if applicable.
```
관련 공공서비스 정보를 찾았지만 사용 가능한 문서만으로 정확한 답을 확인할 수 없으므로, 관련 공공기관에 문의하고 해당되는 경우 다음 서류를 준비하라는 식으로 답한다.

## Fine-Tuning Strategy

GPU 자원이 불확실하므로 MVP가 fine-tuning에 의존해서는 안 된다.

세 단계로 나눈다. 필수 MVP는 fine-tuning 없이 동작해야 하고, 가능하면 가벼운 fine-tuning을 사용하며, 고급 fine-tuning은 메인 워크플로우가 작동한 뒤 선택적으로 고려한다.

1단계는 fine-tuning 없이 프롬프트 템플릿, glossary 정규화, query expansion, 제공 RAG를 사용하는 것이다.

2단계는 가능할 경우 공식 베트남어 질의 재작성, 공공서비스 답변 스타일, glossary 기반 정규화 예시에 대해 가벼운 fine-tuning을 적용하는 것이다.

3단계는 선택적 고급 fine-tuning으로, 소수언어에서 베트남어로의 정규화와 도메인 특화 intent classification을 다룬다.

데모는 반드시 1단계만으로도 작동해야 한다.

## Document Expansion Strategy

ColBERT나 neural document expansion을 핵심 경로로 삼지 않는다.

시간이 허용되면 문서 enrichment를 선택적으로 할 수 있다. 예를 들어 쉬운 베트남어 요약, 공식 행정 키워드, 가능한 사용자 질문, 필요 서류, 관련 기관, 자격 조건, 기한, 수수료를 붙일 수 있다.

이것은 제공 RAG를 대체하는 것이 아니라 공공서비스 접근성을 높이는 메타데이터로 설명해야 한다.

Example document metadata:


```json
{
  "document_id": "birth_registration_001",
  "title": "Procedure for birth registration",
  "simple_summary": "This document explains how to register a child's birth.",
  "official_keywords": [
    "đăng ký khai sinh",
    "giấy khai sinh",
    "ủy ban nhân dân cấp xã"
  ],
  "possible_user_questions": [
    "Where do I register my baby's birth?",
    "What papers do I need for birth registration?",
    "Is there a deadline for birth registration?"
  ]
}
```
이 메타데이터는 문서 ID, 제목, 쉬운 요약, 공식 키워드, 사용자가 물어볼 수 있는 질문을 담는다.


## Evaluation Plan

번역 품질만 평가하지 말고 에이전트 워크플로우 전체를 평가한다.

### 1. Query Rewriting Quality

원래 사용자 질문을 RAG에 바로 넣은 경우와, 정규화 및 확장된 질의를 RAG에 넣은 경우를 비교한다.

평가 지표는 top-k 검색 적중률, 기대한 문서가 나타나는지, 공식 행정 용어가 포함되는지다.

해커톤용으로는 Precision@K와 Recall@K를 모두 계산할 수는 있지만, 라벨링 비용을 고려하면 `Hit@K`와 `Recall@K`를 중심으로 두는 것이 현실적이다.

Precision@K:

```text
top-k 중 relevant 문서 수 / k
```

Recall@K:

```text
top-k 중 relevant 문서 수 / 전체 relevant 문서 수
```

Recall@K를 엄밀하게 계산하려면 각 질문에 대해 관련된 전체 정답 문서 목록이 필요하다. 공공서비스 문서에서는 관련 문서의 범위가 애매할 수 있으므로, 작은 평가셋에 대해 수동으로 gold document set을 정해두는 것이 좋다.

추천 라벨 형식:

```json
{
  "query_id": "birth_001",
  "user_query": "아이가 태어났는데 어디에 신고해?",
  "gold_docs": [
    "birth_registration_procedure",
    "birth_registration_required_documents"
  ],
  "must_have_terms": [
    "đăng ký khai sinh",
    "giấy khai sinh"
  ],
  "expected_intent": "birth_registration"
}
```

발표용 비교는 복잡한 IR 지표보다 before/after가 잘 보이는 형태가 좋다.

```text
Original query -> RAG: Hit@3 = 3/10
Normalized + Expanded query -> RAG: Hit@3 = 8/10
```

Precision@K를 넣는다면 `Precision@3` 정도를 보조 지표로 사용한다. 문서가 적고 라벨이 불완전한 상황에서 `Precision@10`까지 강조하면 오히려 평가가 불안정해 보일 수 있다.

### 2. Grounded Answer Quality

검색된 출처를 함께 제공하여 LLM-as-judge로 평가한다.

기준은 답변이 검색된 문서로 뒷받침되는지, 요구사항을 hallucination하지 않는지, 필요한 단계를 포함하는지, 불확실한 정보와 확인된 사실을 분리하는지다.

추천 rubric:

```text
1. Groundedness
검색 문서에 근거했는가?

2. Completeness
필요한 절차, 서류, 기관, 기한을 포함했는가?

3. No Hallucinated Requirements
문서에 없는 서류, 조건, 비용, 기한을 만들어내지 않았는가?

4. Uncertainty Handling
확인된 정보와 불확실한 정보를 분리했는가?

5. Safety
법률, 체류, 의료, 복지 자격 같은 고위험 내용을 단정하지 않았는가?
```

### 3. Translation / Normalization Quality

소수언어 또는 방언 입력의 경우 source text, glossary match, 생성된 베트남어 질의를 함께 평가한다.

source text 없는 reference-free QE만으로는 의미 보존을 판단하기에 충분하지 않다. source text가 없으면 judge는 유창성은 평가할 수 있지만 번역 충실도는 평가하기 어렵다.

여기서 평가 대상을 "번역 품질"이라고 넓게 잡기보다, "사용자 intent가 공식 베트남어 공공서비스 질의로 잘 보존되었는가"로 잡는 것이 좋다.

추천 rubric:

```text
1. Intent Preservation
사용자의 원래 행정적 필요가 보존되었는가?

2. Official Terminology Accuracy
공식 베트남어 행정 용어가 정확히 사용되었는가?

3. Domain Slot Completeness
대상자, 절차, 서류, 기관, 기한 같은 핵심 slot이 누락되지 않았는가?

4. No Unsupported Assumption
원문에 없는 조건, 자격, 지역, 서류를 임의로 추가하지 않았는가?

5. Retrieval Readiness
생성된 질의가 공공문서 RAG 검색에 적합한가?
```

점수 기준:

```text
5 = 완전히 적절함
4 = 작은 표현 문제는 있으나 사용 가능
3 = 의도는 대체로 맞지만 중요한 누락 또는 모호함 있음
2 = 일부 의도만 맞고 검색 질의로 위험함
1 = 원래 의도와 크게 다름
```

Better judge prompt inputs:

```text
Source user query:
...

Glossary matches:
...

Generated official Vietnamese query:
...

Target public-service domain:
...

Judge whether the generated query preserves the user's intent and includes correct public-service terms.
```
원문 사용자 질문, glossary match, 생성된 공식 베트남어 질의를 함께 제공하고, 사용자 의도가 보존되었는지와 올바른 공공서비스 용어가 포함되었는지 평가하게 한다.
source가 소수언어라 LLM이 직접 이해하기 어려울 수 있으므로, glossary match를 함께 제공해 judge가 의미 보존 여부를 판단할 수 있게 한다.

### 4. User Accessibility

최종 답변이 쉬운 언어를 쓰는지, 공식 용어를 설명하는지, 체크리스트를 제공하는지, 출처를 인용하는지, 근거 없는 주장을 피하는지 평가한다.

추천 rubric:

```text
1. Plain-Language Clarity
비전문가가 이해할 수 있는 쉬운 표현인가?

2. Terminology Explanation
어려운 공식 행정 용어를 설명했는가?

3. Actionability
사용자가 다음 행동을 알 수 있도록 checklist나 단계가 있는가?

4. Source Visibility
출처 문서 또는 근거가 보이는가?

5. Appropriate Fallback
불확실한 경우 기관 문의나 추가 확인을 안내했는가?
```

## Demo Script

### Baseline

사용자의 비공식 표현 또는 소수언어 질문을 RAG에 바로 넣는다.
예상 결과는 약한 검색 결과, 누락된 공식 용어, 혼란스럽거나 불완전한 답변이다.

### Agent Workflow

같은 질문을 전체 에이전트 워크플로우에 통과시킨다.

```text
Language Router
-> Glossary Normalizer
-> Official Query Generator
-> Query Expansion Agent
-> Provided RAG
-> Grounded Answer Composer
-> Plain-Language Response
```

언어 라우터, glossary 정규화, 공식 질의 생성, query expansion, 제공 RAG, 근거 기반 답변 생성, 쉬운 언어 응답 생성을 순서대로 수행한다.
예상 결과는 더 좋은 공식 질의, 더 관련성 높은 검색 문서, 더 명확한 근거 기반 답변, 더 접근성 높은 최종 안내다.

## What To Build First
구현 순서는 하나의 도메인에 대한 작은 glossary, 언어/도메인 라우팅 프롬프트, 공식 베트남어 질의 생성 프롬프트, query expansion 프롬프트, 제공 RAG 연동, 근거 기반 답변 생성기, 최종 응답 포맷터, 5-10개 예시 질문으로 구성된 작은 평가 세트다.

## What Not To Prioritize

커스텀 BM25 구현, 커스텀 벡터 데이터베이스, 메인 검색 시스템으로서의 ColBERT, 넓은 다국어 지원, 대규모 fine-tuning, 품질 안전장치 없는 완전한 소수언어 번역은 우선순위에 두지 않는다.

## Final Architecture Summary

Citizen language layer normalizes minority-language, dialect, and informal expressions.

한국어: 시민 언어 레이어는 소수언어, 방언, 비공식 표현을 정규화한다.

Administrative query layer creates official Vietnamese public-service queries.

한국어: 행정 질의 레이어는 공식 베트남어 공공서비스 질의를 생성한다.

RAG utilization layer uses the provided RAG system effectively.

한국어: RAG 활용 레이어는 제공된 RAG 시스템을 효과적으로 사용한다.

Grounded answer layer composes source-based public-service guidance.

한국어: 근거 기반 답변 레이어는 출처 기반 공공서비스 안내를 작성한다.

Accessibility layer explains the answer in simple language with glossary support.

한국어: 접근성 레이어는 glossary의 도움을 받아 답변을 쉬운 언어로 설명한다.

The key insight:

한국어: 핵심 통찰:

> The value is not in replacing RAG. The value is making RAG usable for people who do not speak in the language of official documents.

한국어: 가치는 RAG를 대체하는 데 있지 않다. 가치는 공식 문서의 언어로 말하지 않는 사람들도 RAG를 사용할 수 있게 만드는 데 있다.
