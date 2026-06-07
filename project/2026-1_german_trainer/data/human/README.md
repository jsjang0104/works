# human 데이터셋

한국인 화자의 실제 독일어 명사구 발화 데이터셋. gTTS 기반 평가의 한계를 보완하기 위해 수집하였으며, `asr/eval/final_evaluate.py`로 파인튜닝 모델을 평가하는 데 사용한다.

## 화자 정보

| 화자 ID | 독일어 숙련도 | 성별 |
|---------|------|------|
| hw_ha   | advanced | 남 |
| jk_hong | advanced | 남 |
| mk_cho  | advanced | 남 |
| mc_park | advanced | 여 |
| js_jang | intermediate | 여 |
| jw_choi | basic | 남 |
| jw_kim  | advanced | 여 |
| kj_lee  | intermediate | 남 |
| ts_ham  | intermediate | 남 |


## 디렉토리 구조

```
human/
├── recording_list.csv   # 녹음 목록 (num / KR / DE / 화자별 점수)
├── convert.py           # m4a 등 원본 음성을 16kHz mono WAV로 변환 (wav/ 생성)
├── hw_ha/wav/
├── jk_hong/wav/
├── js_jang/wav/
├── jw_choi/wav/
├── jw_kim/wav/
├── kj_lee/wav/
├── mc_park/wav/
├── mk_cho/wav/
└── ts_ham/wav/
```

각 화자 폴더의 원본 음성 파일명은 `{화자ID}_{번호}.m4a` (번호는 `recording_list.csv`의 `num`과 대응), `convert.py` 실행 시 같은 이름으로 `wav/{화자ID}_{번호}.wav`에 변환·저장된다 (예: `mk_cho_5.m4a` → `wav/mk_cho_5.wav`).

## recording_list.csv

| 컬럼 | 설명 |
|------|------|
| `num` | 문장 번호 (1~25, 모든 화자 공통) |
| `KR` | 한국어 문장 (발화 지시문) |
| `DE` | 독일어 명사구 정답 (ground truth) |
| `hw_ha` ~ `ts_ham` | 화자별 발화 품질 점수 (Direct Assessment, 1~3, 미평가 시 빈 값) |

문장당 1행, 총 25행. 모든 화자가 동일한 25개 문장을 녹음한다 (행 = 문장, 열 = 화자).

## 녹음 조건

- 휴대폰 음성녹음 앱 사용
- 조용한 실내 환경 권장
- 원본 파일(44100Hz 또는 48000Hz)은 Whisper 입력에 맞게 **16000Hz mono WAV**로 변환 후 저장

## 평가

`asr/eval/final_evaluate.py --data human` (또는 `baseline_evaluate.py --data human`) 실행 시:
- 화자별 / 숙련도 그룹별(advanced / intermediate / basic) WER, Log-Likelihood 계산
- `recording_list.csv`에 점수(score)가 채워진 경우 DA score vs WER / LL Spearman 상관관계 추가 계산
- 결과: `asr/eval/final_result_human.json`, `asr/eval/final_eval_human.png` (baseline은 `baseline_*` 접두)
