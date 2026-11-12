"""Generate a German/Korean MP3 from a vocabulary file, reusing cached clips."""

import argparse
import asyncio
import hashlib
import json
import subprocess
from array import array
from dataclasses import dataclass
from pathlib import Path

if __package__:
    from .vocabulary import load_vocabulary, vocabulary_version
else:
    from vocabulary import load_vocabulary, vocabulary_version

ROOT = Path(__file__).resolve().parent
SAMPLE_RATE = 24000


@dataclass(frozen=True)
class AudioSettings:
    de_voice: str = 'de-DE-KatjaNeural'
    ko_voice: str = 'ko-KR-SunHiNeural'
    de_rate: str = '+10%'
    ko_rate: str = '+5%'
    field_gap_ms: int = 180
    row_gap_ms: int = 550


def build_segments(cards, settings):
    segments = []
    for row, card in enumerate(cards):
        fields = ['term', 'meaning', 'sentence']
        if card.get('sentence_translation'):
            fields.append('sentence_translation')
        for field in fields:
            korean = field in ('meaning', 'sentence_translation')
            voice = settings.ko_voice if korean else settings.de_voice
            rate = settings.ko_rate if korean else settings.de_rate
            text = card[field]
            key = hashlib.sha256(json.dumps([text, voice, rate], ensure_ascii=False).encode()).hexdigest()
            last_field = field == fields[-1]
            gap = settings.row_gap_ms if last_field else settings.field_gap_ms
            if row == len(cards) - 1 and last_field:
                gap = 0
            segments.append(dict(row=row, field=field, text=text, voice=voice,
                                 rate=rate, gap_ms=gap, key=key))
    return segments


def silence_pcm(milliseconds):
    return b'\0\0' * round(SAMPLE_RATE * milliseconds / 1000)


def trim_pcm(pcm):
    """Remove service padding, retaining 15ms around audible samples."""
    samples = array('h')
    samples.frombytes(pcm)
    start = next((i for i, value in enumerate(samples) if abs(value) > 100), None)
    if start is None:
        raise ValueError('음성이 없는 TTS 조각입니다.')
    end = next(i for i in range(len(samples) - 1, -1, -1) if abs(samples[i]) > 100) + 1
    margin = round(SAMPLE_RATE * .015)
    return samples[max(0, start - margin):min(len(samples), end + margin)].tobytes()


def decode_pcm(path):
    import imageio_ffmpeg
    path = Path(path)
    try:
        result = subprocess.run([
            imageio_ffmpeg.get_ffmpeg_exe(), '-hide_banner', '-loglevel', 'error',
            '-xerror', '-i', str(path), '-f', 's16le', '-ar', str(SAMPLE_RATE),
            '-ac', '1', 'pipe:1'], check=True, capture_output=True)
        return trim_pcm(result.stdout)
    except (subprocess.CalledProcessError, ValueError) as error:
        path.unlink(missing_ok=True)
        raise RuntimeError('손상된 음성 캐시를 제거했습니다. 같은 명령을 다시 실행하면 이 조각을 재합성합니다.') from error


async def synthesize(segments, cache, concurrency):
    import edge_tts
    cache.mkdir(parents=True, exist_ok=True)
    jobs = {s['key']: s for s in segments}
    queue = asyncio.Queue()
    for key, segment in jobs.items():
        path = cache / f'{key}.mp3'
        if not path.exists() or path.stat().st_size < 100:
            queue.put_nowait(segment)
    needed = queue.qsize()
    print(f'TTS: {len(jobs)}개 고유 조각 중 {needed}개 생성, {len(jobs) - needed}개 캐시 재사용', flush=True)
    completed = 0

    async def worker():
        nonlocal completed
        while not queue.empty():
            segment = queue.get_nowait()
            target = cache / (segment['key'] + '.mp3')
            temporary = target.with_suffix('.part')
            for attempt in range(5):
                try:
                    await edge_tts.Communicate(segment['text'], segment['voice'],
                                               rate=segment['rate'],
                                               connect_timeout=15, receive_timeout=45).save(str(temporary))
                    if temporary.stat().st_size < 100:
                        raise ValueError('빈 TTS 응답')
                    temporary.replace(target)
                    break
                except Exception:
                    temporary.unlink(missing_ok=True)
                    if attempt == 4:
                        raise
                    await asyncio.sleep(2 ** attempt)
            completed += 1
            if completed % 50 == 0 or completed == needed:
                print(f'TTS: {completed}/{needed}', flush=True)
            queue.task_done()

    tasks = [asyncio.create_task(worker()) for _ in range(concurrency)]
    try:
        await asyncio.gather(*tasks)
    except BaseException:
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        raise


def assemble(cards, segments, cache, output, source_version, settings):
    import imageio_ffmpeg
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    temporary = output.with_suffix('.mp3.part')
    manifest_path = output.with_suffix('.timings.json')
    rows = [dict(id=c['id'], term=c['term'], fields=[]) for c in cards]
    samples_written = 0
    process = subprocess.Popen([
        ffmpeg, '-hide_banner', '-loglevel', 'error', '-y', '-f', 's16le',
        '-ar', str(SAMPLE_RATE), '-ac', '1', '-i', 'pipe:0', '-codec:a', 'libmp3lame',
        '-b:a', '128k', '-metadata', f'title={output.stem} — Deutsch / 한국어',
        '-f', 'mp3', str(temporary)], stdin=subprocess.PIPE)
    try:
        for index, segment in enumerate(segments):
            pcm = decode_pcm(cache / (segment['key'] + '.mp3'))
            row = rows[segment['row']]
            start = samples_written / SAMPLE_RATE
            if segment['field'] == 'term':
                row['start'] = round(start, 4)
            process.stdin.write(pcm)
            samples_written += len(pcm) // 2
            row['fields'].append(dict(field=segment['field'], text=segment['text'],
                                      start=round(start, 4), end=round(samples_written / SAMPLE_RATE, 4)))
            last_in_row = index + 1 == len(segments) or segments[index + 1]['row'] != segment['row']
            if last_in_row:
                row['end'] = round(samples_written / SAMPLE_RATE, 4)
            silence = silence_pcm(segment['gap_ms'])
            process.stdin.write(silence)
            samples_written += len(silence) // 2
            if last_in_row and (segment['row'] + 1) % 100 == 0:
                print(f'MP3 연결: {segment["row"] + 1}/{len(cards)}행', flush=True)
        process.stdin.close()
        code = process.wait()
        if code:
            raise RuntimeError(f'FFmpeg 인코딩 실패: {code}')
        # Decode the complete result before publishing either output file.
        subprocess.run([ffmpeg, '-v', 'error', '-i', str(temporary), '-f', 'null', '-'], check=True)
        manifest = dict(source_version=source_version, rows_count=len(cards),
                        duration_seconds=round(samples_written / SAMPLE_RATE, 4),
                        sample_rate=SAMPLE_RATE, settings=settings.__dict__, rows=rows)
        manifest_temp = manifest_path.with_suffix('.json.part')
        manifest_temp.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        temporary.replace(output)
        manifest_temp.replace(manifest_path)
    except BaseException:
        if process.poll() is None:
            process.kill()
        process.wait()
        temporary.unlink(missing_ok=True)
        raise
    print(f'완료: {output} ({samples_written / SAMPLE_RATE / 60:.1f}분, {len(cards)}행)', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, help='기본값: 입력 파일 옆의 같은 이름 MP3')
    parser.add_argument('--cache-dir', type=Path, default=ROOT / '.tts-cache')
    parser.add_argument('--de-voice', default='de-DE-KatjaNeural')
    parser.add_argument('--ko-voice', default='ko-KR-SunHiNeural')
    parser.add_argument('--de-rate', default='+10%')
    parser.add_argument('--ko-rate', default='+5%')
    parser.add_argument('--field-gap-ms', type=int, default=180)
    parser.add_argument('--row-gap-ms', type=int, default=550)
    parser.add_argument('--concurrency', type=int, default=6)
    args = parser.parse_args()
    if not 1 <= args.concurrency <= 12:
        parser.error('--concurrency는 1~12여야 합니다.')
    if args.field_gap_ms < 0 or args.row_gap_ms <= args.field_gap_ms:
        parser.error('행 간 공백은 항목 간 공백보다 길어야 합니다.')
    settings = AudioSettings(args.de_voice, args.ko_voice, args.de_rate, args.ko_rate,
                             args.field_gap_ms, args.row_gap_ms)
    source_version = vocabulary_version(args.input)
    cards = load_vocabulary(args.input)
    segments = build_segments(cards, settings)
    cache = args.cache_dir.resolve()
    asyncio.run(synthesize(segments, cache, args.concurrency))
    if vocabulary_version(args.input) != source_version:
        raise RuntimeError('생성 중 단어장이 바뀌었습니다. 다시 실행하세요. 캐시는 보존됩니다.')
    output = (args.output or args.input.with_suffix('.mp3')).resolve()
    assemble(cards, segments, cache, output, source_version, settings)


if __name__ == '__main__':
    main()
