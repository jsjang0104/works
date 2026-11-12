"""Strict vocabulary reader shared by audio generation and study apps."""

import hashlib
from collections import Counter
from pathlib import Path


def vocabulary_version(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_vocabulary(path):
    path = Path(path)
    cards = []
    occurrences = Counter()
    for number, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        if not line.strip():
            continue
        fields = [field.strip() for field in line.split('|')]
        if len(fields) not in (3, 4) or not all(fields):
            raise ValueError(f'{path.name} {number}행: 독일어 | 한국어 뜻 | 독일어 예문 [| 예문 한국어 해석] 형식이 필요합니다.')
        term, meaning, sentence = fields[:3]
        sentence_translation = fields[3] if len(fields) == 4 else ''
        digest = hashlib.sha256('\x1f'.join(fields).encode('utf-8')).hexdigest()[:20]
        occurrences[digest] += 1
        cards.append(dict(id=f'{digest}-{occurrences[digest]}', term=term,
                          meaning=meaning, sentence=sentence,
                          sentence_translation=sentence_translation))
    if not cards:
        raise ValueError('단어장이 비어 있습니다.')
    return cards
