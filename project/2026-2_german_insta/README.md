# 2026-2 어휘와구문 B2 과제 (German Words and Sentences B2 Assignment)

## 과제 내용

한국외국어대학교 독일어과 전공인 [어휘와 구문 B2](https://wis.hufs.ac.kr/src08/jsp/lecture/syllabus.jsp?mode=print&ledg_year=2026&ledg_sessn=3&org_sect=A&lssn_cd=A03224202)에서는 매주 교수님께서 정해주시는 독일어 단어를 사용하여 독일어 문장 2개를 작문한 뒤, 관련 이미지와 함께 인스타그램에 업로드해야 한다.

## 과제 자동화 계획

위 과제 내용을 자동화하는 개인용 Python 터미널 도구를 개발한다. 

1. 독일어 단어 2개를 터미널에 입력하면 로컬 google/gemma-4-31b-it로 B1~B2 수준의 독일어 문장과 한국어 해석 초안을 만든다. (GPU를 사용할 수 없거나 로딩·추론이 실패하면 독일어 문장과 한국어 해석을 직접 입력)
2. 확정된 문장으로 Hugging Face의 FLUX Space MCP에서 이미지를 만든다. 
3. rule-based script를 이용하여 단어·독일어 문장·한국어 해석·생성 날짜를 코드로 합성한 이미지 카드 2장과 게시용 캡션을 저장한다. 
4. 인스타그램에는 사용자가 직접 업로드한다. 

## 파일 구조

```text
2026-2_german_insta/
├── README.md                  # 사용 방법과 과제 설명
├── main.py                    # 터미널 입력과 전체 실행 흐름
├── settings.py                # 모델, MCP, 글꼴, 시간 제한 설정
├── local_llm.py               # GPU 확인과 로컬 Gemma 문장·해석 생성
├── image_mcp.py               # FLUX MCP 이미지 생성과 다운로드
├── cards.py                   # 카드 합성, 고정 캡션, 날짜별 저장
├── requirements.txt           # 기본 실행 패키지
├── requirements-local.txt     # 로컬 Gemma 실행용 추가 패키지
├── requirements-dev.txt       # 테스트·코드 검사용 패키지 (개발용)
├── pyproject.toml             # pytest·Ruff 설정 (개발용)
├── .gitignore                 # 가상환경·캐시를 Git에서 제외
├── fonts/
│   ├── NotoSansKR-VF.ttf      # 한국어 해석용 글꼴
│   └── OFL.txt                # 글꼴 라이선스
├── tests/                     # 수정 후 동작을 확인하는 자동 테스트 (개발용)
│   ├── test_cards.py          # 카드 배치와 캡션·파일 저장
│   ├── test_cli.py            # 옵션 없는 실행과 재실행
│   ├── test_image_mcp.py      # MCP 응답과 이미지 처리
│   ├── test_local_llm.py      # GPU 판정과 모델 실패 처리
│   └── test_workflow.py       # 입력·문장 확인·오류 복구 흐름
├── 2026-MM-DD/                # 해당 날짜에 만든 과제 결과물 (실행 시 자동 생성)
└── .venv/                     # 이 서버의 Python 가상환경 (Git 제외)
```

## 실행 방법

```bash
cd ~/Workspace/works/project/2026-2_german_insta
.venv/bin/python main.py
```

### MCP 이미지 프롬프트

```text
Create a warm, detailed editorial illustration of this German sentence. No text or lettering in the image. Never include any words, letters, captions, signs, speech bubbles, signatures, or watermarks. Scene: [확정한 독일어 문장]
```

기본 분위기는 따뜻하고 섬세한 삽화다. 생성 이미지 안에는 글자를 절대 넣지 않도록 영어로 지시하고, 자막·표지판·말풍선·서명·워터마크도 제외하도록 요청한다. 삽화의 분위기는 이 함수에서 수정할 수 있다. 카드의 단어·문장·한국어 해석·생성 날짜는 Pillow가 합성한다.

## 설정과 구성

기본값은 [settings.py](settings.py)에서 수정한다.

| 항목 | 기본 동작 |
| --- | --- |
| 로컬 모델 | 캐시된 `google/gemma-4-31B-it`; 다른 스냅샷은 `MODEL_PATH` 지정 |
| 캐시 탐색 | `HF_HUB_CACHE`, `HF_HOME`, `/home/shared/hf_cache`, 사용자 기본 캐시 |
| GPU | 기존 계산 작업이 없고 여유 메모리가 24 GiB 이상인 GPU 한 장 선택; `CUDA_VISIBLE_DEVICES` 존중 |
| 모델 로딩 | 4-bit NF4, 로컬 파일만 사용; 별도 프로세스에서 최대 240초 실행 |
| 이미지 생성 | [evalstate/flux1_schnell](https://huggingface.co/spaces/evalstate/flux1_schnell)의 `flux1_schnell_infer` MCP 도구 |
| 이미지 요청 | 1024×768, 4 steps; MCP 호출 제한 시간 180초 |
| 문장·이미지 프롬프트·캡션 | 독일어 문장과 한국어 해석을 로컬 LLM으로 함께 생성; 확정된 문장으로 이미지 프롬프트를 구성하고 캡션은 고정 문구로 저장 |
