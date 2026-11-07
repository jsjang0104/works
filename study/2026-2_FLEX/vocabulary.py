"""Shared, strict reader for the vocabulary used by the quiz and speech script."""

import hashlib
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WORD_FILE = ROOT / 'Wort.md'


def vocabulary_version(path=WORD_FILE):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_vocabulary(path=WORD_FILE):
    cards = []
    occurrences = Counter()
    for number, line in enumerate(Path(path).read_text(encoding='utf-8').splitlines(), 1):
        if not line.strip():
            continue
        fields = [field.strip() for field in line.split('|')]
        if len(fields) != 3 or not all(fields):
            raise ValueError(f'Wort.md {number}행: 독일어 | 한국어 뜻 | 독일어 예문 형식이 필요합니다.')
        term, meaning, sentence = fields
        digest = hashlib.sha256('\x1f'.join(fields).encode('utf-8')).hexdigest()[:20]
        occurrences[digest] += 1
        cards.append(dict(id=f'{digest}-{occurrences[digest]}', term=term,
                          meaning=meaning, sentence=sentence))
    if not cards:
        raise ValueError('단어장이 비어 있습니다.')
    return cards
