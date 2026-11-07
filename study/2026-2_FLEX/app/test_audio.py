import unittest

from generate_audio import AudioSettings, build_segments, silence_pcm, trim_pcm


class AudioTests(unittest.TestCase):
    def test_preserves_every_field_and_short_vs_long_gaps(self):
        cards = [dict(id='a', term='Bad', meaning='중성 욕실', sentence='Das Bad ist klein.'),
                 dict(id='b', term='Bahn', meaning='여성 기차', sentence='Die Bahn kommt.')]
        segments = build_segments(cards, AudioSettings())
        self.assertEqual([s['text'] for s in segments],
                         ['Bad', '중성 욕실', 'Das Bad ist klein.', 'Bahn', '여성 기차', 'Die Bahn kommt.'])
        self.assertEqual([s['gap_ms'] for s in segments], [180, 180, 550, 180, 180, 0])
        self.assertTrue(segments[0]['voice'].startswith('de-DE-'))
        self.assertTrue(segments[1]['voice'].startswith('ko-KR-'))

    def test_cache_identity_includes_voice_text_and_rate(self):
        cards = [dict(id='a', term='Bad', meaning='중성 욕실', sentence='Das Bad ist klein.')]
        a = build_segments(cards, AudioSettings())
        b = build_segments(cards, AudioSettings(de_rate='+20%'))
        self.assertNotEqual(a[0]['key'], b[0]['key'])
        self.assertEqual(a[1]['key'], b[1]['key'])

    def test_silence_and_trimming_keep_non_silent_speech(self):
        from array import array
        speech = array('h', [1000, -1000] * 500).tobytes()
        padding = silence_pcm(400)
        result = trim_pcm(padding + speech + padding)
        self.assertIn(speech, result)
        self.assertLess(len(result), len(padding + speech + padding))
        self.assertEqual(len(silence_pcm(180)), 8640)
        with self.assertRaises(ValueError):
            trim_pcm(padding)

    def test_corrupt_cache_is_removed_so_the_next_run_can_recover(self):
        import tempfile
        from pathlib import Path
        from generate_audio import decode_pcm
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'broken.mp3'
            path.write_bytes(b'x' * 150)
            with self.assertRaisesRegex(RuntimeError, '다시 실행'):
                decode_pcm(path)
            self.assertFalse(path.exists())


if __name__ == '__main__':
    unittest.main()
