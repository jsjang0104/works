"""Local FLEX quiz server. Start with: .venv/bin/python server.py"""

import argparse

from flask import Flask, jsonify, send_from_directory

from vocabulary import ROOT, WORD_FILE, load_vocabulary, vocabulary_version


def create_app(word_file=WORD_FILE):
    app = Flask(__name__, static_folder=None)

    @app.get('/')
    def index():
        return send_from_directory(ROOT / 'static', 'index.html')

    @app.get('/static/<name>')
    def static_file(name):
        if name not in {'app.mjs', 'quiz.mjs', 'style.css'}:
            return '', 404
        return send_from_directory(ROOT / 'static', name)

    @app.get('/api/cards')
    def cards():
        try:
            response = jsonify(cards=load_vocabulary(word_file), version=vocabulary_version(word_file))
            response.headers['Cache-Control'] = 'no-store'
            return response
        except (ValueError, OSError) as error:
            return jsonify(error=str(error)), 422

    @app.get('/Wort.mp3')
    def audio():
        return send_from_directory(ROOT, 'Wort.mp3', conditional=True)

    @app.after_request
    def headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; "
            "connect-src 'self'; media-src 'self'; img-src 'self' data:; "
            "object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
        return response

    return app


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8765)
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error('포트는 1~65535여야 합니다.')
    print(f'FLEX 단어장: http://127.0.0.1:{args.port}', flush=True)
    create_app().run(host='127.0.0.1', port=args.port, debug=False)
