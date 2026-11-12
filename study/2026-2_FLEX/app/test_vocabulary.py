import tempfile
import unittest
from pathlib import Path

from vocabulary import load_vocabulary, vocabulary_version


class VocabularyTests(unittest.TestCase):
    def read(self, text):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'Wort.md'
            path.write_text(text, encoding='utf-8')
            return load_vocabulary(path), vocabulary_version(path)

    def test_preserves_gender_meaning_order_and_duplicate_rows(self):
        cards, version = self.read('Bahn | 여성 기차 | Die Bahn kommt.\n\nBahn | 여성 기차 | Die Bahn kommt.\n')
        self.assertEqual(len(cards), 2)
        self.assertEqual(cards[0]['meaning'], '여성 기차')
        self.assertNotEqual(cards[0]['id'], cards[1]['id'])
        self.assertEqual(len(version), 64)

    def test_reports_malformed_row_number(self):
        with self.assertRaisesRegex(ValueError, '2행'):
            self.read('Bad | 중성 욕실 | Das Bad ist klein.\nkaputt | 망가진\n')

    def test_rejects_missing_fields_and_empty_deck(self):
        for text in ['Bad | | Das Bad ist klein.', '\n\n',
                     'Bad | 욕실 | Das Bad ist klein. | ',
                     'Bad | 욕실 | Das Bad ist klein. | 욕실은 작다. | extra']:
            with self.assertRaises(ValueError):
                self.read(text)

    def test_preserves_sentence_translation_and_includes_it_in_identity(self):
        a, va = self.read('Bahn | 기차 | Die Bahn kommt. | 기차가 온다.\n')
        b, vb = self.read('Bahn | 기차 | Die Bahn kommt. | 기차가 도착한다.\n')
        self.assertEqual(a[0]['sentence_translation'], '기차가 온다.')
        self.assertNotEqual(a[0]['id'], b[0]['id'])
        self.assertNotEqual(va, vb)

    def test_shuffle_round_trip_preserves_optional_sentence_translations(self):
        from shuffle_vocabulary import arrange, format_vocabulary
        cards, _ = self.read('Bahn | 기차 | Die Bahn kommt. | 기차가 온다.\n'
                             'Bad | 욕실 | Das Bad ist klein.\n')
        text = format_vocabulary(arrange(cards, seed=42))
        result, _ = self.read(text)
        by_term = {card['term']: card for card in result}
        self.assertEqual(by_term['Bahn']['sentence_translation'], '기차가 온다.')
        self.assertEqual(by_term['Bad']['sentence'], 'Das Bad ist klein.')
        self.assertEqual(by_term['Bad']['sentence_translation'], '')

    def test_version_changes_with_content(self):
        a, va = self.read('Bad | 중성 욕실 | Das Bad ist klein.')
        b, vb = self.read('Bad | 중성 욕실 | Das Bad ist groß.')
        self.assertNotEqual(va, vb)
        self.assertNotEqual(a[0]['id'], b[0]['id'])


if __name__ == '__main__':
    unittest.main()
