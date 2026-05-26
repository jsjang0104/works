import csv
import hashlib
import io
import re
import tempfile

import gradio as gr
from lingua import Language, LanguageDetectorBuilder
from transformers import pipeline

try:
    import hanja as _hanja
    _HANJA_OK = True
except ImportError:
    _HANJA_OK = False

MODEL_ID = "jsjang0104/book-genre-classifier-bert"

LABEL_MAP = {
    "LABEL_0": "Geschichte",
    "LABEL_1": "Literatur",
    "LABEL_2": "Sozialwissenschaften",
    "LABEL_3": "Sprachwissenschaft",
}

CATEGORY_KO = {
    "Geschichte": "역사",
    "Literatur": "문학",
    "Sprachwissenschaft": "어학",
    "Sozialwissenschaften": "사회과학",
    "Sozialwissenschaft": "사회과학",
    "Sonstiges": "기타",
}

CATEGORY_CODE = {
    "sprachwissenschaft": "SP",
    "sozialwissenschaften": "SZ",
    "sozialwissenschaft": "SZ",
    "sonstiges": "S",
    "geschichte": "G",
    "literatur": "L",
}

_UMLAUT = {
    "ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss",
    "Ä": "Ae", "Ö": "Oe", "Ü": "Ue",
}

classifier = pipeline("text-classification", model=MODEL_ID)

_LINGUA_MAP = {
    Language.GERMAN: "DE",
    Language.KOREAN: "KR",
    Language.ENGLISH: "EN",
}

_lang_detector = LanguageDetectorBuilder.from_languages(*_LINGUA_MAP.keys()).build()

_DE_MARKERS = {
    "und", "der", "die", "das", "von", "zu", "im", "mit",
    "auf", "über", "nach", "vor", "bei", "aus", "wer", "wie",
    "was", "ein", "eine", "des", "dem", "den", "zum", "zur",
}

def detect_language(text: str) -> str:
    # 한글 포함 시 KR
    if re.search(r"[가-힣]", text):
        return "KR"
    # 움라우트/에스체트 포함 시 DE
    if re.search(r"[äöüßÄÖÜ]", text):
        return "DE"
    # 독일어 고빈도 단어 포함 시 DE
    words = set(re.findall(r"[a-zA-Z]+", text.lower()))
    if words & _DE_MARKERS:
        return "DE"
    # fallback: lingua
    result = _lang_detector.detect_language_of(text)
    return _LINGUA_MAP.get(result, "ETC")


def preprocess(text: str) -> str:
    if not text:
        return ""
    result = "".join(_UMLAUT.get(c, c) for c in text)
    if _HANJA_OK:
        result = _hanja.translate(result, "substitution")
    return result.strip().lower()


def hash5(text: str) -> str:
    if not text:
        return "00000"
    n = int(hashlib.md5(text.encode()).hexdigest(), 16)
    return f"{n % 100000:05d}"


def get_category_code(cat_proc: str) -> str:
    return CATEGORY_CODE.get(cat_proc, cat_proc.upper() if cat_proc else "S")


def build_call_number(title, author, location, category_de, language, seq=1):
    loc_p = preprocess(location)
    title_p = preprocess(title)
    author_p = preprocess(author)
    cat_p = preprocess(category_de)
    lang_p = preprocess(language)
    th = hash5(title_p)
    ah = hash5(author_p)
    cc = get_category_code(cat_p)
    return f"{loc_p}_{th}_{ah}_{cc}_{lang_p}_{seq}"


def predict_single(title, author, location, category):
    if not title.strip():
        return "제목을 입력해주세요.", "", ""
    if not author.strip():
        return "저자를 입력해주세요.", "", ""
    if not location.strip():
        return "위치(Location)를 입력해주세요.", "", ""

    score_text = ""
    if category.strip():
        category_de = category.strip()
    else:
        pred = classifier(title)[0]
        category_de = LABEL_MAP.get(pred["label"], pred["label"])
        score_text = f"   신뢰도: {pred['score']:.1%}"

    category_ko = CATEGORY_KO.get(category_de, category_de)
    language = detect_language(title)
    call_number = build_call_number(title, author, location, category_de, language, seq=1)
    genre_text = f"{category_de}  ({category_ko}){score_text}"
    return genre_text, language, call_number, "AVAILABLE"


def process_csv(file):
    if file is None:
        return None, "CSV 파일을 업로드해주세요."

    file_path = file.name if hasattr(file, "name") else file
    with open(file_path, "r", encoding="utf-8-sig") as f:
        content = f.read()

    reader = csv.DictReader(io.StringIO(content))
    if reader.fieldnames:
        reader.fieldnames = [n.strip() for n in reader.fieldnames]

    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(["call_number", "title", "author", "status", "language", "location", "category"])

    counter = {}
    count = 0

    for row in reader:
        title = row.get("title", "").strip()
        author = row.get("author", "").strip()
        if not title and not author:
            continue

        loc = row.get("location", "").strip()
        if not loc:
            continue

        cat_raw = row.get("category", "").strip()
        if not cat_raw:
            pred = classifier(title or author)[0]
            cat_raw = LABEL_MAP.get(pred["label"], pred["label"])

        language = detect_language(title or author)

        loc_p = preprocess(loc)
        title_p = preprocess(title)
        author_p = preprocess(author)
        cat_p = preprocess(cat_raw)
        lang_p = preprocess(language)

        th = hash5(title_p)
        ah = hash5(author_p)
        cc = get_category_code(cat_p)

        key = (th, ah, cc, lang_p)
        counter[key] = counter.get(key, 0) + 1

        call_number = f"{loc_p}_{th}_{ah}_{cc}_{lang_p}_{counter[key]}"
        cat_ko = CATEGORY_KO.get(cat_raw, cat_raw)
        writer.writerow([call_number, title, author, "AVAILABLE", language, loc, cat_ko])
        count += 1
        if count % 100 == 0:
            print(f"[진행] {count}건 처리 완료", flush=True)

    tmp = tempfile.NamedTemporaryFile(
        delete=False, suffix=".csv", mode="w", encoding="utf-8-sig", newline=""
    )
    tmp.write(out.getvalue())
    tmp.close()

    return tmp.name, f"✅ {count}건 처리 완료"


with gr.Blocks(title="오스트리아 도서관 — 장르 분류 & 청구기호 생성") as demo:
    gr.Markdown(
        "# 오스트리아 도서관 — 장르 분류 & 청구기호 생성\n"
        "BERT 모델로 도서 장르를 분류하고, 청구기호를 자동 생성합니다.\n\n"
        "**분류 카테고리**: Geschichte(역사) · Literatur(문학) · "
        "Sozialwissenschaften(사회과학) · Sprachwissenschaft(어학)"
    )

    with gr.Tab("단건 입력"):
        with gr.Row():
            with gr.Column():
                t_title    = gr.Textbox(label="제목 (Title) *", placeholder="예: Faust")
                t_author   = gr.Textbox(label="저자 (Author) *", placeholder="예: Goethe")
                t_location = gr.Textbox(label="위치 (Location) *", placeholder="예: A1-4")
                t_category = gr.Textbox(label="분야 (Category)", placeholder="비워두면 자동 분류 — 예: Literatur")
                btn = gr.Button("분류 및 청구기호 생성", variant="primary")
            with gr.Column():
                out_genre    = gr.Textbox(label="예측 장르")
                out_language = gr.Textbox(label="감지 언어 (Language)")
                out_call     = gr.Textbox(label="청구기호 (call_number)")
                out_status   = gr.Textbox(label="상태", value="AVAILABLE", interactive=False)

        btn.click(
            fn=predict_single,
            inputs=[t_title, t_author, t_location, t_category],
            outputs=[out_genre, out_language, out_call, out_status],
        )

    with gr.Tab("CSV 일괄 처리"):
        gr.Markdown(
            "CSV 파일을 업로드하면 청구기호를 일괄 생성해 다운로드합니다.\n\n"
            "- `category` 열이 비어 있으면 모델이 자동으로 장르를 예측합니다.\n"
            "- 필수 열: `title`, `author`, `location` / 선택 열: `category`\n"
            "- `call_number`, `language`, `status`는 자동으로 설정됩니다."
        )
        csv_input = gr.File(label="CSV 업로드", file_types=[".csv"])
        csv_btn   = gr.Button("청구기호 생성", variant="primary")
        csv_out   = gr.File(label="결과 CSV 다운로드")
        csv_msg   = gr.Textbox(label="처리 결과", interactive=False)

        csv_btn.click(
            fn=process_csv,
            inputs=[csv_input],
            outputs=[csv_out, csv_msg],
        )

demo.launch(server_name="0.0.0.0", server_port=7860)
