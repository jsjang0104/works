import tempfile
import unittest
from pathlib import Path

from server import create_app


class ServerTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.path = Path(self.directory.name) / 'Wort.md'
        self.path.write_text('Bad | 중성 욕실 | Das Bad ist klein.\n', encoding='utf-8')
        self.client = create_app(self.path).test_client()

    def tearDown(self):
        self.directory.cleanup()

    def test_serves_deck_and_static_screen(self):
        response = self.client.get('/api/cards')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['cards'][0]['term'], 'Bad')
        self.assertIn('no-store', response.headers['Cache-Control'])
        for path in ['/', '/static/quiz.mjs']:
            with self.client.get(path) as response:
                self.assertEqual(response.status_code, 200)

    def test_never_serves_project_source_or_virtual_environment(self):
        for path in ['/server.py', '/.venv/pyvenv.cfg', '/static/quiz.test.mjs', '/Wort.md']:
            self.assertEqual(self.client.get(path).status_code, 404)

    def test_invalid_data_has_useful_message(self):
        self.path.write_text('broken', encoding='utf-8')
        response = self.client.get('/api/cards')
        self.assertEqual(response.status_code, 422)
        self.assertIn('1행', response.json['error'])


if __name__ == '__main__':
    unittest.main()
