# noun-phrases 데이터셋

독일어 명사구 발화 데이터셋. `grammar/declension.py`로 생성한 명사구를 gTTS로 합성하여 Whisper 파인튜닝 및 평가에 사용한다.

## 디렉토리 구조

```
noun-phrases/
├── prepare.py          # 데이터 생성 스크립트
├── train/
│   ├── wav/            # 학습용 음성 (2,888개)
│   └── transcripts.csv
├── val/
│   ├── wav/            # 검증용 음성 (361개)
│   └── transcripts.csv
└── test/
    ├── wav/            # 평가용 음성 (361개)
    └── transcripts.csv
```

**총 3,610개** (원래 10,000개 목표였으나 gTTS 429 rate limit으로 3,610개에서 중단, 8:1:1로 분할)

## transcripts.csv 컬럼

| 컬럼 | 설명 |
|------|------|
| `filename` | wav 파일명 (0000.wav 형식) |
| `transcript` | 독일어 명사구 원문 |
| `korean` | 대응 한국어 문장 |
| `gender` | 화자 성별 시뮬레이션 (`male` / `female`) |
| `speed` | 발화 속도 배율 (0.80 – 0.95) |
| `pitch` | 피치 배율 (male: 0.88–0.94 / female: 1.06–1.13) |

## prepare.py

`grammar/declension.py`의 `generate_phrase()`로 명사구를 생성하고 gTTS로 음성을 합성하는 스크립트.

**실행 방법**

```bash
pip install gtts pydub
sudo apt install ffmpeg
python data/noun-phrases/prepare.py
```

**주요 동작**

- `random.Random(42)`으로 고정 시드 셔플 → 재실행해도 동일한 순서 보장
- 각 샘플마다 속도(0.80–0.95×)와 성별(피치)을 무작위 적용하여 다양성 확보
  - 속도/피치 변환은 pydub의 `frame_rate` 트릭 사용 (리샘플링 없이 재생 속도 조절)
- 중단 후 재실행 시 기존 wav가 있는 항목은 건너뜀 (이어받기 지원)
- gTTS 429 에러 발생 시 60초 대기 후 재시도

**오디오 처리 파이프라인**

```
gTTS MP3 → pydub AudioSegment → speed 조절 → pitch 조절 → 16kHz mono WAV
```

## 명사구 구조

`grammar/declension.py`가 생성하는 명사구의 형태:

```
[정관사/부정관사/지시사] + [형용사] + [명사]
```

4격 (Nominativ / Akkusativ / Dativ / Genitiv) 및 3성 (남성 / 여성 / 중성) + 복수를 조합하여 격변화가 반영된 명사구를 무작위 생성한다.
