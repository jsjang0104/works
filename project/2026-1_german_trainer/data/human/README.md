# human 데이터셋

한국인 화자의 실제 독일어 명사구 발화 데이터셋. gTTS 기반 평가의 한계를 보완하기 위해 수집하였으며, `asr/final_evaluation.py`로 파인튜닝 모델을 평가하는 데 사용한다.

## 화자 정보

| 화자 ID | 그룹 | 성별 |
|---------|------|------|
| hw_ha   | good | 남 |
| jk_hong | good | 남 |
| mk_cho  | good | 남 |
| mc_park | good | 여 |
| js_jang | poor | 여 |
| jw_choi | poor | 남 |
| jw_kim  | good | 여 |

- **good**: 독일어에 능숙한 한국인 화자
- **poor**: 독일어를 잘 못하는 한국인 화자 (장단음, 강세 등 미숙)

## 디렉토리 구조

```
human/
├── recording_list.csv   # 녹음 목록 (speaker / KR / DE)
├── hw_ha/wav/
├── jk_hong/wav/
├── js_jang/wav/
├── jw_choi/wav/
├── mc_park/wav/
└── mk_cho/wav/
```

각 화자 폴더의 wav 파일은 `recording_list.csv`의 해당 화자 행 순서대로 `0000.wav`, `0001.wav`, ... 로 명명한다.

## recording_list.csv

| 컬럼 | 설명 |
|------|------|
| `speaker` | 화자 ID |
| `KR` | 한국어 문장 (발화 지시문) |
| `DE` | 독일어 명사구 정답 (ground truth) |

6명 × 25문장 = 총 150행. 모든 화자가 동일한 25개 문장을 녹음한다.

## 녹음 조건

- 휴대폰 음성녹음 앱 사용
- 조용한 실내 환경 권장
- 원본 파일(44100Hz 또는 48000Hz)은 Whisper 입력에 맞게 **16000Hz mono WAV**로 변환 후 저장

## 평가

`asr/final_evaluation.py` 실행 시:
- 화자별 / 그룹별(good vs poor) WER 계산
- Character-level confusion matrix 시각화 (전체 + 화자별)
- 결과: `asr/human_eval_result.json`, `asr/human_eval_wer.png`, `asr/human_eval_confusion_*.png`
