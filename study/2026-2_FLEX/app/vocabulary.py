"""FLEX vocabulary paths and defaults for the shared reader."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WORD_FILE = ROOT.parent / 'Wort.md'

sys.path.insert(0, str(ROOT.parent.parent))
from tts_module.vocabulary import load_vocabulary as _load_vocabulary
from tts_module.vocabulary import vocabulary_version as _vocabulary_version


def vocabulary_version(path=WORD_FILE):
    return _vocabulary_version(path)


def load_vocabulary(path=WORD_FILE):
    return _load_vocabulary(path)
