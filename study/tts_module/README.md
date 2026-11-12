# 공부 자료 TTS

시, 읽기 자료, 단어장 등 여러 과목의 텍스트를 MP3로 만드는 공용 모듈이다. 입력 파일, 출력 경로, 낭독할 언어를 명령으로 지정한다. 기본 음성은 독일어와 한국어다.

## 설치

아래 명령은 `study/tts_module/`에서 실행한다.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

**새 음성을 만들 때에는 선택한 낭독 내용이 Microsoft 음성 서비스로 전송되며 인터넷 연결이 필요하다.** [edge-tts](https://github.com/rany2/edge-tts)를 사용하며 API 키는 필요 없다.

## 읽기 자료·시

독일어 원문 아래에 한국어 번역이 있는 마크다운에서 독일어만 읽을 때:

```bash
.venv/bin/python generate_audio.py --input ../2026-2_lesen/Lektion9.md --format markdown --language de --output ../2026-2_lesen/audio/Lektion9.mp3
```

다른 공부 자료도 `--input`, `--output` 경로를 바꿔 같은 방식으로 실행한다. 일반 텍스트 파일도 사용할 수 있다.

```bash
.venv/bin/python generate_audio.py --input ../과목명/본문.txt --format text --language de --output ../과목명/audio/본문.mp3
```

- `--language de`: 독일어만 낭독한다.
- `--language ko`: 한국어만 낭독한다.
- `--language all`: 두 언어를 원문에 나온 순서대로 낭독한다. 기본값이다.
- 병기 자료는 독일어와 한국어를 서로 다른 줄에 쓴다. 한글이 포함된 줄은 한국어, 나머지 글자 줄은 독일어 음성으로 처리한다. 언어 선택도 이 구분을 따른다.
- 마크다운의 제목 내용은 읽고, 제목·인용·목록·강조 표시와 로마 숫자 연 번호, 구분선, 코드 블록 등은 낭독에서 제외한다.
- 각 내용 줄 사이에 기본 `550ms`의 공백을 둔다.

출처, 작성자, 메모처럼 읽지 않을 구간은 다음처럼 표시한다. 이 구간은 문서 화면에는 보이지만 낭독에서는 제외한다.

```markdown
<!-- tts:skip:start -->
작성자·출처·학습 메모
<!-- tts:skip:end -->
```

## 단어장

각 행을 다음 3열 또는 4열 형식으로 작성한다.

```text
독일어 단어 | 한국어 뜻 | 독일어 예문
독일어 단어 | 한국어 뜻 | 독일어 예문 | 예문 한국어 해석
```

```bash
.venv/bin/python generate_audio.py --input ../과목명/단어장.md --format vocabulary --output ../과목명/audio/단어장.mp3
```

기본 순서는 단어 → 뜻 → 독일어 예문 → 예문 한국어 해석이다. `--language de`는 단어와 독일어 예문만, `--language ko`는 뜻과 예문 해석만 읽는다.

## 입력·출력

| 옵션 | 동작 |
| --- | --- |
| `--input` | 필수. 입력 자료 경로 |
| `--format auto` | 기본값. 첫 내용 줄이 3·4열이면 단어장, 그 외 `.md`·`.markdown`은 마크다운, 나머지는 일반 텍스트 |
| `--format vocabulary / markdown / text` | 입력 형식을 직접 지정 |
| `--output` | MP3 출력 경로. 상위 폴더가 없으면 생성 |
| 출력 경로 생략 | 입력 파일 옆에 같은 이름의 MP3 생성 |

MP3 옆에 같은 이름의 `.timings.json`도 저장한다. 낭독한 텍스트, 언어, 음성, 속도와 시간 정보가 들어간다.

## 음성·속도·공백

| 항목 | 기본값 | 옵션 |
| --- | --- | --- |
| 독일어 음성 | `de-DE-KatjaNeural` | `--de-voice` |
| 한국어 음성 | `ko-KR-SunHiNeural` | `--ko-voice` |
| 독일어 속도 | 기본 대비 `+10%` | `--de-rate` |
| 한국어 속도 | 기본 대비 `+5%` | `--ko-rate` |
| 단어장 항목 사이 무음 | `180ms` | `--field-gap-ms` |
| 다음 행까지 무음 | `550ms` | `--row-gap-ms` |
| 출력 | MP3, 24kHz, 모노, 128kbps | |

```bash
.venv/bin/python generate_audio.py --input ../과목명/본문.md --language de --de-rate=+0% --row-gap-ms 700
```

## 캐시·재실행

- 음성 조각은 이 모듈의 `.tts-cache/`에 저장한다. 과목이 달라도 내용·음성·속도가 같으면 재사용한다.
- `--cache-dir`로 캐시 위치를 바꿀 수 있다.
- 생성이 중단되면 같은 명령을 다시 실행한다. 완성된 조각은 다시 만들지 않는다.
- 병렬 요청 수는 기본 6개이며 `--concurrency`로 1~12개를 지정한다. 서비스 응답이 불안정하면 2개로 줄인다.

## 검증

```bash
.venv/bin/python -m unittest discover -v
```
