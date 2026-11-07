# FLEX 독일어

출처: **FLEX UP 독일어** (유덕근, 최경인)

## 가상환경과 실행

퀴즈 프로그램, 음성 파일, 가상환경은 `app/`에 있다. 단어장은 상위 폴더의 `Wort.md`를 그대로 사용한다.

먼저 `2026-2_FLEX/`에서 프로그램 폴더로 이동한다. 아래의 나머지 명령은 모두 `app/` 안에서 실행한다.

```bash
cd app
```

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python server.py
```

이미 만든 가상환경을 이용할 때는 다음 한 줄이면 됨

```bash
.venv/bin/python server.py
```

접속 주소: **http://127.0.0.1:8765**


```bash
.venv/bin/python server.py --port 8766
```

서버는 내 컴퓨터의 `127.0.0.1`에서만 접속할 수 있다. 별도 배포는 없으며, 퀴즈 실행에는 인터넷이 필요 없다.

## 퀴즈 사용법

- 단축키: 
    - `Space` 또는 `Enter`로 뜻 확인
    - `1` 또는 `←`로 실패, `2` 또는 `→`로 성공. 

## MP3

`app/Wort.mp3`는 단어장 940행을 담은 **약 75.9분, 72.9MB**의 파일. 단어장 순서대로 다음을 반복

```text
독일어 단어/숙어 → 짧은 공백 → 한국어 뜻 → 짧은 공백 → 독일어 예문 → 다음 행까지 공백
```

- 사용 프로그램은 [edge-tts](https://github.com/rany2/edge-tts)다. Microsoft Edge의 온라인 TTS를 Python에서 이용하며 API 키가 필요 없음. 
- **음성을 새로 만들 때에는 단어·뜻·예문이 Microsoft 음성 서비스로 전송되며 인터넷 연결이 필요.** 

| 항목 | 설정 |
| --- | --- |
| 독일어 음성 | `de-DE-KatjaNeural` |
| 한국어 음성 | `ko-KR-SunHiNeural` |
| 독일어 속도 | 기본 대비 `+15%` |
| 한국어 속도 | 기본 대비 `+5%` |
| 단어·뜻·예문 사이 무음 | `180ms` |
| 다음 행까지 무음 | `550ms` |
| 출력 | MP3, 24kHz, 모노, 128kbps |

같은 파일을 다시 만들 때:

```bash
.venv/bin/python generate_audio.py
```

속도·공백을 바꾸려면:

```bash
.venv/bin/python generate_audio.py --de-rate=+20% --ko-rate=+10% --field-gap-ms 150 --row-gap-ms 500
```

- 음성 변경은 `--de-voice`, `--ko-voice`, 병렬 요청 수는 `--concurrency`로 설정 
- 기본 병렬 요청 수는 6개. 
- 서비스 응답이 불안정하면 `--concurrency 2`로 줄여 실행한다. 사용 가능한 음성은 `.venv/bin/edge-tts --list-voices`로 확인한다.

## 순서 다시 섞기

```bash
.venv/bin/python shuffle_vocabulary.py
.venv/bin/python generate_audio.py
```

유사 어휘 그룹은 유지하면서 그룹의 순서를 새로 섞는다. 같은 순서를 재현하려면 `--seed 20261106`처럼 숫자를 지정한다. 현재 파일을 바탕으로 섞으므로 같은 입력과 같은 seed일 때 같은 결과가 나온다. 단어장 순서를 바꾸면 퀴즈 진도가 초기화되며, MP3도 다시 연결해야 새 순서와 일치한다.

## 검증

Python 테스트는 추가 테스트 패키지 없이 실행. 퀴즈 상태 전환 테스트에는 Node.js 18 이상이 필요하며, 사이트 사용에는 Node.js가 필요 없음.

```bash
.venv/bin/python -m unittest discover -v
node --test static/quiz.test.mjs
```

확인 항목: 단어장 형식과 중복 행 식별, 언어별 음성과 공백, API 응답, 실패 단어의 다음 사이클 이동, 중복 채점 방지, 새로고침 복원, 잘못된 저장 데이터 초기화.
