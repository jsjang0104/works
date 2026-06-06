"""
declension.py로 독일어 명사구 10000개를 생성하고
gTTS로 음성을 합성하여 train/val/test로 분할합니다.

분할: train 8000 / val 1000 / test 1000
중단 후 재실행 시 이미 생성된 파일은 건너뜁니다.

필요 패키지:
    pip install gtts pydub
ffmpeg 필요 (sudo apt install ffmpeg)
"""

import csv
import io
import os
import sys
import time
import random

from gtts import gTTS
from pydub import AudioSegment

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'grammar'))
from declension import generate_phrase

# ── 설정 ──────────────────────────────────────────────────────────────────────

TOTAL       = 10000
N_TRAIN     = 8000
N_VAL       = 1000
N_TEST      = 1000
SAMPLE_RATE = 16000
SLEEP_SEC   = 1.5    # gTTS rate limit 방지
RETRY_429   = 60     # 429 발생 시 대기 시간 (초)

SPEED_RANGE = (0.80, 0.95)

PITCH_RANGE = {
    "male":   (0.88, 0.94),
    "female": (1.06, 1.13),
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SPLITS   = {
    "train": N_TRAIN,
    "val":   N_VAL,
    "test":  N_TEST,
}

# ── TTS 변환 ──────────────────────────────────────────────────────────────────

def tts_to_wav(text: str, wav_path: str, retries: int = 5) -> tuple:
    speed  = random.uniform(*SPEED_RANGE)
    gender = random.choice(["male", "female"])
    pitch  = random.uniform(*PITCH_RANGE[gender])

    for attempt in range(retries):
        try:
            tts = gTTS(text=text, lang="de")
            mp3_buf = io.BytesIO()
            tts.write_to_fp(mp3_buf)
            mp3_buf.seek(0)

            audio = AudioSegment.from_mp3(mp3_buf).set_channels(1)

            audio = audio._spawn(
                audio.raw_data,
                overrides={"frame_rate": int(audio.frame_rate * speed)}
            ).set_frame_rate(SAMPLE_RATE)

            audio = audio._spawn(
                audio.raw_data,
                overrides={"frame_rate": int(SAMPLE_RATE * pitch)}
            ).set_frame_rate(SAMPLE_RATE)

            audio.export(wav_path, format="wav")
            return gender, round(speed, 3), round(pitch, 3)

        except Exception as e:
            is_429 = "429" in str(e)
            wait   = RETRY_429 if is_429 else 3 * (attempt + 1)
            if attempt < retries - 1:
                print(f"  [retry {attempt+1}/{retries}] {'429 rate limit' if is_429 else str(e)} — {wait}s 대기")
                time.sleep(wait)
            else:
                raise e

# ── 구 생성 (고정 시드로 재실행해도 동일 순서) ──────────────────────────────

print(f"Generating {TOTAL} phrases ...")
rng     = random.Random(42)
phrases = [generate_phrase() for _ in range(TOTAL)]
rng.shuffle(phrases)

# ── 분할 & 저장 ───────────────────────────────────────────────────────────────

offset = 0
for split, n in SPLITS.items():
    wav_dir  = os.path.join(BASE_DIR, split, "wav")
    csv_path = os.path.join(BASE_DIR, split, "transcripts.csv")
    os.makedirs(wav_dir, exist_ok=True)

    subset = phrases[offset:offset + n]
    offset += n

    # 이미 완료된 파일 목록 로드 (이어받기)
    done = set()
    if os.path.exists(csv_path):
        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames and "filename" in reader.fieldnames:
                for row in reader:
                    done.add(row["filename"])

    remaining = n - len(done)
    print(f"\n[{split}] {n} samples ({len(done)} already done, {remaining} remaining) ...")

    if remaining == 0:
        print(f"  → 전부 완료됨, 건너뜀")
        continue

    csv_mode = "a" if done else "w"
    with open(csv_path, csv_mode, newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not done:
            writer.writerow(["filename", "transcript", "korean", "gender", "speed", "pitch"])

        for i, phrase in enumerate(subset):
            wav_name = f"{i:04d}.wav"
            if wav_name in done:
                continue

            text   = phrase["german"]
            korean = phrase["korean"]
            wav_path_out = os.path.join(wav_dir, wav_name)

            gender, speed, pitch = tts_to_wav(text, wav_path_out)
            writer.writerow([wav_name, text, korean, gender, speed, pitch])
            f.flush()
            time.sleep(SLEEP_SEC)

            done.add(wav_name)
            if len(done) % 500 == 0:
                print(f"  {len(done)}/{n} done")

    print(f"  → {csv_path}")

print("\nAll done.")
