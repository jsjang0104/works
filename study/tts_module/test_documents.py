import tempfile
import unittest
from pathlib import Path

from documents import load_material


class DocumentTests(unittest.TestCase):
    def read(self, text, *, input_format='auto', language='all', suffix='.md'):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / ('Material' + suffix)
            path.write_text(text, encoding='utf-8')
            return load_material(path, input_format=input_format, language=language)

    def test_german_only_markdown_excludes_translations_stanza_numbers_and_notes(self):
        cards = self.read('# 9. Der Weg\n> 길\n\n## I.\n'
                          'Das Wasser fließt.\n> 물이 흐른다.\n'
                          '## II.\n**Der Stein bleibt.**\n> 돌은 남는다.\n'
                          '<!-- tts:skip:start -->\nBertolt Brecht, 1938\n'
                          '[Quelle](https://example.com)\n<!-- tts:skip:end -->\n',
                          language='de')
        self.assertEqual([card['text'] for card in cards],
                         ['Der Weg', 'Das Wasser fließt.', 'Der Stein bleibt.'])
        self.assertTrue(all(card['language'] == 'de' for card in cards))

    def test_bilingual_markdown_preserves_language_and_order(self):
        text = '# Der Weg\n> 길\nDas Wasser fließt.\n> 물이 흐른다.\n'
        cards = self.read(text)
        self.assertEqual([card['language'] for card in cards], ['de', 'ko', 'de', 'ko'])
        self.assertEqual([card['text'] for card in self.read(text, language='ko')],
                         ['길', '물이 흐른다.'])

    def test_existing_vocabulary_is_detected_and_still_validated(self):
        cards = self.read('Bahn | 기차 | Die Bahn kommt. | 기차가 온다.\n')
        self.assertEqual(cards[0]['sentence_translation'], '기차가 온다.')
        with self.assertRaisesRegex(ValueError, '2행'):
            self.read('Bahn | 기차 | Die Bahn kommt.\nbroken\n')

    def test_plain_text_preserves_content_and_duplicate_identity(self):
        cards = self.read('Das Wasser fließt.\nDas Wasser fließt.\n', suffix='.txt')
        self.assertEqual([card['text'] for card in cards],
                         ['Das Wasser fließt.', 'Das Wasser fließt.'])
        self.assertNotEqual(cards[0]['id'], cards[1]['id'])

    def test_empty_language_selection_is_rejected(self):
        with self.assertRaisesRegex(ValueError, '읽을 내용'):
            self.read('# 한국어 제목\n한국어 본문\n', language='de')

    def test_comments_and_skip_examples_inside_code_cannot_hide_following_prose(self):
        for content in ('<!-- opening comment', '<!-- tts:skip:start -->'):
            with self.subTest(content=content):
                cards = self.read('# Titel\n```html\n' + content +
                                  '\n```\nDas ist der Text.\n', language='de')
                self.assertEqual([card['text'] for card in cards], ['Titel', 'Das ist der Text.'])

    def test_fences_only_close_with_enough_matching_markers_and_no_info_string(self):
        for opening, false_close, closing in (
                ('````markdown', '```', '````'),
                ('```python', '```python', '```'),
                ('~~~~text', '~~~', '~~~~')):
            with self.subTest(opening=opening):
                cards = self.read('# Titel\n' + opening + '\nCode eins\n' + false_close +
                                  '\nCode zwei\n' + closing + '\nDas ist der Text.\n', language='de')
                self.assertEqual([card['text'] for card in cards], ['Titel', 'Das ist der Text.'])


if __name__ == '__main__':
    unittest.main()
