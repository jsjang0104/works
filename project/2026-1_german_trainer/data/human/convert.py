"""
오디오 파일을 16kHz mono WAV로 변환하고 앞뒤 무음을 제거합니다.

사용법:
    python convert.py js_jang
    python convert.py js_jang jw_choi hw_ha

- 화자 폴더 내 오디오 파일(m4a / mp3 / wav)을 파일명 기준 알파벳 순으로 정렬
- wav/ 서브폴더에 기존 파일명을 유지한 채 확장자만 .wav로 바꿔 저장 (예: mk_cho_1.m4a → mk_cho_1.wav)
- ffmpeg 필요 (sudo apt install ffmpeg)
"""

import argparse
import os
import sys

from pydub import AudioSegment
from pydub.silence import detect_nonsilent

SAMPLE_RATE     = 16000
SILENCE_THRESH  = -40    # dBFS
MIN_SILENCE_LEN = 100    # ms — 이보다 짧은 무음은 자르지 않음
PADDING_MS      = 50     # 무음 제거 후 양쪽에 남길 여백 (ms)
AUDIO_EXTS      = {".m4a", ".mp3", ".wav", ".flac", ".ogg"}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def trim_silence(audio: AudioSegment) -> AudioSegment:
    chunks = detect_nonsilent(audio, min_silence_len=MIN_SILENCE_LEN, silence_thresh=SILENCE_THRESH)
    if not chunks:
        return audio
    start = max(0, chunks[0][0] - PADDING_MS)
    end   = min(len(audio), chunks[-1][1] + PADDING_MS)
    return audio[start:end]


def convert_speaker(speaker: str):
    speaker_dir = os.path.join(BASE_DIR, speaker)
    wav_dir     = os.path.join(speaker_dir, "wav")

    if not os.path.isdir(speaker_dir):
        print(f"[ERROR] 폴더 없음: {speaker_dir}")
        return

    files = sorted(
        f for f in os.listdir(speaker_dir)
        if os.path.splitext(f)[1].lower() in AUDIO_EXTS
    )

    if not files:
        print(f"[{speaker}] 오디오 파일 없음")
        return

    os.makedirs(wav_dir, exist_ok=True)
    print(f"[{speaker}] {len(files)}개 변환 시작 → {wav_dir}")

    for fname in files:
        stem    = os.path.splitext(fname)[0]
        out_name = f"{stem}.wav"
        src  = os.path.join(speaker_dir, fname)
        dst  = os.path.join(wav_dir, out_name)

        audio = AudioSegment.from_file(src)
        audio = audio.set_channels(1).set_frame_rate(SAMPLE_RATE)
        audio = trim_silence(audio)
        audio.export(dst, format="wav")

        duration = len(audio) / 1000
        print(f"  {fname} → {out_name}  ({duration:.2f}s)")

    print(f"[{speaker}] 완료\n")


def main():
    parser = argparse.ArgumentParser(description="오디오 변환 스크립트")
    parser.add_argument("speakers", nargs="+", help="화자 폴더명 (예: js_jang jw_choi)")
    args = parser.parse_args()

    for speaker in args.speakers:
        convert_speaker(speaker)


if __name__ == "__main__":
    main()
