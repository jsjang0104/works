# 독일어·한국어 단어장 TTS

`독일어 | 한국어 뜻 | 독일어 예문 | 예문 한국어 해석` 형식의 단어장을 MP3 하나로 만든다. 단어장마다 `--input`으로 입력 파일을 지정한다. 예문 해석이 없는 기존 3열 형식도 사용할 수 있다.

각 행은 독일어 단어 → 한국어 뜻 → 독일어 예문 → 예문 한국어 해석 순서로 읽는다. 예문 해석은 한국어 음성과 속도를 사용하며, 해석 뒤에 다음 행까지의 공백을 둔다.

## 가상환경과 실행

아래 명령은 `study/tts_module/`에서 실행한다.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python generate_audio.py --input ../2026-2_FLEX/Wort.md
```

기본 출력은 입력 파일 옆의 같은 이름 MP3와 시간 정보 JSON이다. 위 명령은 `../2026-2_FLEX/Wort.mp3`와 `../2026-2_FLEX/Wort.timings.json`을 만든다. 출력 위치를 직접 정할 때는 `--output 경로.mp3`를 지정한다.

**음성을 새로 만들 때에는 단어·뜻·예문·해석이 Microsoft 음성 서비스로 전송되며 인터넷 연결이 필요하다.** [edge-tts](https://github.com/rany2/edge-tts)를 사용하며 API 키는 필요 없다.

## 음성 설정

| 항목 | 기본값 |
| --- | --- |
| 독일어 음성 | `de-DE-KatjaNeural` |
| 한국어 음성 | `ko-KR-SunHiNeural` |
| 독일어 속도 | 기본 대비 `+10%` |
| 한국어 속도 | 기본 대비 `+5%` |
| 항목 사이 무음 | `180ms` |
| 다음 행까지 무음 | `550ms` |
| 출력 | MP3, 24kHz, 모노, 128kbps |

```bash
.venv/bin/python generate_audio.py --input ../2026-2_FLEX/Wort.md --de-rate=+5% --ko-rate=+5% --field-gap-ms 180 --row-gap-ms 550
```

- 음성은 `--de-voice`, `--ko-voice`로 바꾼다.
- 기본 병렬 요청 수는 6개이며, `--concurrency`로 1~12개를 지정한다.
- 음성 조각은 이 폴더의 `.tts-cache/`에 저장한다. 내용·음성·속도가 같은 조각은 재사용하며, `--cache-dir`로 캐시 위치를 바꿀 수 있다.
- 생성이 중단되면 같은 명령을 다시 실행한다. 완성된 캐시를 재사용한다.
- 단어장을 읽는 `vocabulary.py`는 FLEX 퀴즈에서도 함께 사용한다.

## 검증

```bash
.venv/bin/python -m unittest discover -v
```
