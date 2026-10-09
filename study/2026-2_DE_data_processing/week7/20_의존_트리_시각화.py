# displaCy로 의존 트리를 HTML 파일로 저장합니다.
# 브라우저에서 열어 토큰 간 화살표(의존 관계)를 시각적으로 확인할 수 있습니다.

import spacy
from spacy import displacy
from pathlib import Path

nlp = spacy.load("de_core_news_sm")
doc = nlp("Die Professorin erklärt den Studierenden die deutsche Syntax sehr geduldig.")

# style="dep": 의존구문 트리 시각화 / page=True: 완전한 HTML 페이지로 렌더링
html = displacy.render(doc, style="dep", page=True)
out_path = Path("dependency_tree.html")
out_path.write_text(html, encoding="utf-8")  # UTF-8로 저장 (독일어 특수문자 보존)

print(f"시각화 저장 완료: {out_path}")
