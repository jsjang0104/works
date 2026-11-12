"""Read study material as vocabulary rows or lines of Markdown/plain text."""

import hashlib
import json
import re
from collections import Counter
from pathlib import Path

if __package__:
    from .vocabulary import load_vocabulary
else:
    from vocabulary import load_vocabulary


def load_material(path, input_format='auto', language='all'):
    path = Path(path)
    lines = path.read_text(encoding='utf-8-sig').splitlines()
    if input_format == 'auto':
        first = next((line.strip() for line in lines if line.strip()), '')
        if len(first.split('|')) in (3, 4):
            input_format = 'vocabulary'
        else:
            input_format = 'markdown' if path.suffix.lower() in ('.md', '.markdown') else 'text'
    if input_format == 'vocabulary':
        cards = load_vocabulary(path)
        if language != 'all':
            for card in cards:
                fields = ['term', 'meaning', 'sentence']
                if card.get('sentence_translation'):
                    fields.append('sentence_translation')
                card['speech_fields'] = [field for field in fields
                                         if (field in ('meaning', 'sentence_translation')) == (language == 'ko')]
        return cards

    cards = []
    occurrences = Counter()
    skipped = False
    comment = False
    fence = None
    for line in lines:
        text = line.strip()
        if input_format == 'markdown' and fence is not None:
            if len(text) >= len(fence) and set(text) == {fence[0]}:
                fence = None
            continue
        if text == '<!-- tts:skip:start -->':
            skipped = True
            continue
        if text == '<!-- tts:skip:end -->':
            skipped = False
            continue
        if skipped or not text:
            continue
        if input_format == 'markdown':
            if comment:
                comment = '-->' not in text
                continue
            if text.startswith('<!--') and '-->' not in text:
                comment = True
                continue
            text = re.sub(r'<!--.*?-->', '', text).strip()
            marker = re.match(r'^(`{3,}|~{3,})', text)
            if marker:
                fence = marker[1]
                continue
            if re.match(r'^(?:[-*_]\s*){3,}$', text) or re.match(r'^\[[^\]]+\]:', text):
                continue
            if text.startswith('![') or re.match(r'^(?:https?://|www\.)', text):
                continue
            text = re.sub(r'^#{1,6}\s+', '', text)
            text = re.sub(r'^(?:>\s*)+', '', text)
            text = re.sub(r'^[-*+]\s+', '', text)
            text = re.sub(r'^\d+[.)]\s+', '', text)
            text = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', text)
            text = re.sub(r'<[^>]+>', '', text)
            text = text.translate(str.maketrans('', '', '*_`~')).strip()
            if re.fullmatch(r'[IVXLCDM]+\.?', text):
                continue
        if not any(char.isalpha() for char in text):
            continue
        text_language = 'ko' if re.search(r'[가-힣ㄱ-ㅎㅏ-ㅣ]', text) else 'de'
        if language != 'all' and text_language != language:
            continue
        digest = hashlib.sha256(json.dumps([text_language, text], ensure_ascii=False).encode()).hexdigest()[:20]
        occurrences[digest] += 1
        cards.append(dict(id=f'{digest}-{occurrences[digest]}', term=text,
                          text=text, language=text_language))
    if not cards:
        raise ValueError('선택한 언어로 읽을 내용이 없습니다.')
    return cards
