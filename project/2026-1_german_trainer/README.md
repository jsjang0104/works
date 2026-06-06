# 🇩🇪 German Declension Trainer

독일어 어미변화(관사·형용사·명사) 말하기 연습 자동화 프로그램

## 배경

외국어로서 독일어를 배우는 한국인 학습자의 주요 말하기 병목 지점은 **관사·형용사·명사의 어미변화**다.
명사의 성(Genus), 수(Numerus), 격(Kasus)에 따라 어미가 달라지는데, 이를 즉각적으로 산출하는 데 익숙하지 않은 학습자는 응답 지연이 발생한다.

기존 튜터링 방식(튜터가 한국어 문장 제시 → 튜티가 독일어로 발화)은 개인별 진행으로 인해 시간 효율이 낮았다.
본 프로젝트는 이 과정을 자동화하여 학습자가 혼자서도 반복 연습할 수 있는 환경을 제공한다.

## 시스템 구조

```
한국어 문장 제시 (텍스트)
        ↓
사용자 독일어 음성 입력
        ↓
ASR 모델 → 텍스트 변환
        ↓
규칙 기반 정답과 비교
        ↓
시각적 피드백 (정/오 표시)
```

## 기능

- A1, A2 수준 단어 범위 내에서 관사·형용사·명사 조합을 랜덤 출제
- 화면에 한국어 문장 제시 (예: `이 작은 개가`) → 사용자가 독일어로 발화 (예: `dieser kleine Hund`)
- ASR로 발화 인식 후 규칙 기반 정답과 비교하여 정/오 판정
- Confusion matrix 기반 모델 평가

## 프로젝트 구조

```
german-declension-trainer/
│
├── asr/
│   ├── baseline.py           # 베이스라인 성능 측정
│   ├── finetune.py           # Whisper fine-tuning
│   └── evaluate.py           # confusion matrix 평가
│
├── grammar/ 
│
├── app.py               # Gradio UI
│
│
├── README.md
└── requiremnets.txt
```

## 기술 스택

| 구성요소 | 내용 |
|---------|------|
| ASR 모델 | Whisper (tiny 베이스, 독일어 fine-tuning) |
| 정답 생성 | 규칙 기반 (강변화/약변화/혼합변화 테이블) |
| UI | Gradio |
| 배포 | Hugging Face Spaces |

## 데이터셋


## 개발 순서

1. 기획
2. Whisper 베이스라인 테스트 → fine-tuning 방향 결정
3. 데이터 준비 + fine-tuning (필요 시)
4. 단어 DB 및 규칙 기반 정답 생성 코딩
5. 채점 로직 코딩
6. Gradio UI 연결
7. HF Spaces 배포
8. Evaluation (confusion matrix)

## 평가

ASR 모델이 독일어 어미를 정확히 인식하는지를 문장 단위 정/오로 판정하여 confusion matrix로 평가한다.
베이스라인 모델과 fine-tuned 모델의 성능을 비교한다.

## 참고

- 본 프로젝트는 멀티모달개론 기말 프로젝트로 제작되었습니다.
- 어미변화 규칙은 Duden 기준 표준 독일어를 따릅니다.
