"""
독일어 명사구 발음 트레이너 - Gradio 인터페이스

사용:  python app.py
모델:  jsjang0104/whisper-tiny-german (HF Hub)
문법:  grammar/declension.py → generate_phrase()
"""

import os
import re
import sys

import gradio as gr
import numpy as np
import torch
from transformers import WhisperForConditionalGeneration, WhisperProcessor

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, "grammar"))
from declension import generate_phrase  # noqa: E402

# ── 모델 로드 ──────────────────────────────────────────────────────────────────

MODEL_DIR   = "jsjang0104/whisper-tiny-german"
SAMPLE_RATE = 16000

device    = "cuda" if torch.cuda.is_available() else "cpu"
processor = WhisperProcessor.from_pretrained(MODEL_DIR)
model     = WhisperForConditionalGeneration.from_pretrained(MODEL_DIR).to(device)
model.eval()
print(f"[app] model on {device} | {MODEL_DIR}")

# ── 헬퍼 ──────────────────────────────────────────────────────────────────────

def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\säöüß]", "", text)
    return re.sub(r"\s+", " ", text).strip()


BLUE = "#2563eb"


def html_highlight(base: str, inflected: str) -> str:
    """공통 접두사 이후 어미를 파란색으로 강조."""
    i = 0
    b, f = base.lower(), inflected.lower()
    while i < len(b) and i < len(f) and b[i] == f[i]:
        i += 1
    stem, ending = inflected[:i], inflected[i:]
    if ending:
        return f'{stem}<span style="color:{BLUE};font-weight:800">{ending}</span>'
    return stem


def highlight_phrase(phrase: dict) -> str:
    words = phrase["german"].split()
    bases = [phrase["hint"][0][:-1], phrase["hint"][1][:-1], phrase["hint"][2]]
    parts = [html_highlight(b, w) for b, w in zip(bases, words)]
    parts += words[len(bases):]
    return " ".join(parts)


def korean_html(phrase: dict) -> str:
    """한국어 문장 HTML — 조사를 파란색으로 강조."""
    text     = phrase["korean"]
    particle = phrase.get("particle", "")
    if particle and text.endswith(particle):
        base    = text[: -len(particle)]
        content = f'{base}<span style="color:{BLUE};font-weight:800">{particle}</span>'
    else:
        content = text
    return (
        f'<div style="font-size:3.2em;font-weight:700;text-align:center;padding:28px 0">'
        f'{content}</div>'
    )


def compute_ll(audio_tuple, ref_text: str):
    if audio_tuple is None:
        return None
    sr, audio = audio_tuple
    if audio.dtype == np.int16:
        audio = audio.astype(np.float32) / 32768.0
    elif audio.dtype != np.float32:
        audio = audio.astype(np.float32)
    if sr != SAMPLE_RATE:
        try:
            import librosa
            audio = librosa.resample(audio, orig_sr=sr, target_sr=SAMPLE_RATE)
        except ImportError:
            pass
    inputs    = processor(audio, sampling_rate=SAMPLE_RATE, return_tensors="pt").to(device)
    label_ids = processor.tokenizer(
        normalize(ref_text), return_tensors="pt"
    ).input_ids.to(device)
    with torch.no_grad():
        loss = model(input_features=inputs.input_features, labels=label_ids).loss
    return round(-loss.item(), 4)


def ll_label(ll: float) -> str:
    if ll >= -0.5:  return "🌟 매우 좋음"
    if ll >= -1.0:  return "✅ 좋음"
    if ll >= -2.0:  return "🔶 보통"
    return "❌ 개선 필요"


LL_PASS = -1.0

IMAGES_DIR  = os.path.join(BASE_DIR, "images")
ADJ_IMAGES  = [os.path.join(IMAGES_DIR, f"adj_{i}.png") for i in (1, 2, 3)]
NOUN_IMAGES = [os.path.join(IMAGES_DIR, f"noun_{i}.png") for i in (1, 2, 3, 4, 5)]
ADJ_PDF     = os.path.join(IMAGES_DIR, "adjective.pdf")
NOUN_PDF    = os.path.join(IMAGES_DIR, "noun.pdf")

# ── Gradio UI ─────────────────────────────────────────────────────────────────

INIT_STATE = {
    "n_questions": 10, "phrases": [], "current_idx": 0,
    "results": [], "hint_text": "", "pending_score": False,
}

CSS = """
#site-header           { text-align:center; padding:24px 0 16px; border-bottom:1px solid #e0e0e0; margin-bottom:8px; }
#site-header h1        { font-size:1.55em; font-weight:700; margin:0 0 6px; }
#site-header .creators { font-size:0.95em; color:#555; margin:0 0 3px; }
#site-header .dept     { font-size:0.82em; color:#888; margin:0; }

#grammar-btns { justify-content:center; gap:16px; margin-top:18px; }
#grammar-hint { text-align:center; color:#888; font-size:0.92em; margin-top:14px; }
#grammar-gallery .gallery { justify-content:center; }

#korean-text  { font-size:3.2em; font-weight:700; text-align:center; padding:28px 0; }
#hint-box     { font-size:1.2em; letter-spacing:0.08em; color:#888; text-align:center; }
#score-box    { font-size:1.3em; text-align:center; padding:16px 0; }
#progress     { text-align:right; color:#aaa; }

/* interactive=False인 ctx-btn은 완전히 숨김 (visibility 토글 버그 우회) */
.ctx-btn:has(button:disabled) { display:none!important; }
"""

HEADER_HTML = """
<div id="site-header">
  <h1>Speech-Based German Declension Training System</h1>
  <p class="creators">Created by: Jungi Hong (Concept &amp; Linguistics) &middot; Jisoo Jang (Digital Implementation)</p>
  <p class="dept">Department of German, Hankuk University of Foreign Studies</p>
</div>
"""

with gr.Blocks(title="German Declension Trainer") as demo:
    state = gr.State(dict(INIT_STATE))

    gr.HTML(HEADER_HTML)

    # ── 1. 설정 화면 ───────────────────────────────────────────────────────────
    with gr.Column(visible=True) as setup_col:
        gr.Markdown(
            "주어지는 한국어 어구를 독일어로 번역해 발화하세요.  \n"
            "파인튜닝된 Whisper 모델이 발음의 정확도를 채점합니다."
        )
        gr.Markdown(
            "첫 번째 문제 채점은 AI 모델 로딩으로 인해 약간 시간이 걸릴 수 있습니다.  \n"
            "한 번 모델이 로드되면, 이후에는 정상 속도로 채점이 진행됩니다."
        )
        n_radio   = gr.Radio(choices=[10, 20, 30], value=10, label="문제 수 선택")
        start_btn = gr.Button("시작하기 →", variant="primary", size="lg")

        with gr.Row(elem_id="grammar-btns"):
            adj_grammar_btn  = gr.Button("참고: 독일어 형용사류 어미변화 규칙")
            noun_grammar_btn = gr.Button("참고: 독일어 명사 형태변화 유형")
        grammar_hint_md = gr.Markdown(
            "이미지를 클릭하면 확대됩니다", visible=False, elem_id="grammar-hint",
        )
        adj_gallery = gr.Gallery(
            value=ADJ_IMAGES, visible=False, label="형용사류 어미변화",
            columns=3, elem_id="grammar-gallery",
        )
        adj_pdf_file = gr.File(
            value=ADJ_PDF, visible=False, label="📄 형용사류 어미변화 규칙 PDF 다운로드",
        )
        noun_gallery = gr.Gallery(
            value=NOUN_IMAGES, visible=False, label="명사 형태변화",
            columns=3, elem_id="grammar-gallery",
        )
        noun_pdf_file = gr.File(
            value=NOUN_PDF, visible=False, label="📄 명사 형태변화 유형 PDF 다운로드",
        )

    # ── 2. 퀴즈 + 결과 화면 (단일 컬럼) ──────────────────────────────────────
    # result_col을 별도로 두지 않고 quiz_col 안에서 전환.
    # visible=False → True 전환 버그를 피하기 위해 결과 섹션도 항상 DOM에 존재.
    with gr.Column(visible=False) as quiz_col:

        # ── 퀴즈 섹션 ────────────────────────────────────────────────────────
        progress_md   = gr.Markdown("", elem_id="progress")
        korean_md     = gr.HTML("", elem_id="korean-text")
        hint_md       = gr.Markdown("", elem_id="hint-box")
        hint_btn      = gr.Button("💡 힌트", size="lg", elem_classes=["ctx-btn"])
        gr.Markdown("---")
        go_record_btn = gr.Button("🎙 녹음하기", variant="primary", size="lg", elem_classes=["ctx-btn"])
        audio_input   = gr.Audio(
            sources=["microphone"], type="numpy", label="녹음", visible=False,
        )
        score_btn  = gr.Button("채점하기", variant="primary", size="lg", interactive=False, elem_classes=["ctx-btn"])
        score_box  = gr.HTML("", elem_id="score-box")
        next_btn   = gr.Button("다음 문제 →", variant="secondary", interactive=False, elem_classes=["ctx-btn"])

        # ── 결과 섹션 (항상 DOM 존재, 퀴즈 중엔 비어있음) ────────────────────
        result_md   = gr.Markdown("")
        restart_btn = gr.Button("처음으로", variant="secondary", interactive=False, elem_classes=["ctx-btn"])

    # ── 이벤트 핸들러 ──────────────────────────────────────────────────────────

    # 공통 출력 목록
    QUIZ_OUTS = [
        state, setup_col, quiz_col,
        progress_md, korean_md, hint_md,
        hint_btn, go_record_btn, audio_input,
        score_btn, score_box, next_btn,
        result_md, restart_btn,
    ]

    def _to_question(new_state, n, idx, phrase):
        """질문 화면 업데이트 튜플 (QUIZ_OUTS 순서)."""
        return (
            new_state,
            gr.update(visible=False),             # setup_col
            gr.update(visible=True),              # quiz_col
            f"**{idx + 1} / {n}**",              # progress_md
            korean_html(phrase),                 # korean_md
            "",                                  # hint_md
            gr.update(interactive=True),          # hint_btn      (CSS로 표시)
            gr.update(interactive=True),          # go_record_btn (CSS로 표시)
            gr.update(visible=False, value=None), # audio_input
            gr.update(interactive=False),         # score_btn     (CSS로 숨김)
            gr.update(value=""),                  # score_box
            gr.update(interactive=False),         # next_btn      (CSS로 숨김)
            "",                                  # result_md (비움)
            gr.update(interactive=False),         # restart_btn   (CSS로 숨김)
        )

    def on_start(n_questions, _state):
        phrases   = [generate_phrase() for _ in range(n_questions)]
        new_state = {**INIT_STATE, "n_questions": n_questions, "phrases": phrases}
        return _to_question(new_state, n_questions, 0, phrases[0])

    def on_hint(st):
        phrase = st["phrases"][st["current_idx"]]
        parts  = "  ".join(phrase["hint"])
        tag    = phrase.get("tag", "")
        text   = f"**힌트:** {parts}" + (f"  `{tag}`" if tag else "")
        return text, {**st, "hint_text": text}

    def on_go_record(st):
        hint_text = st.get("hint_text", "")
        return (
            gr.update(interactive=False),       # go_record_btn  (CSS로 숨김)
            gr.update(interactive=False),       # hint_btn       (CSS로 숨김)
            gr.update(visible=True, value=None),# audio_input
            gr.update(interactive=True),        # score_btn      (CSS로 표시)
            hint_text,                          # hint_md (힌트 유지)
            gr.update(value=""),                # score_box
            gr.update(interactive=False),       # next_btn       (CSS로 숨김)
        )

    def _do_score(audio, st):
        phrase = st["phrases"][st["current_idx"]]
        ll     = compute_ll(audio, phrase["german"])
        if ll is None:
            return (
                gr.update(value="<p>⚠️ 채점 중 오류가 발생했습니다.</p>"),
                gr.update(interactive=False),
                st,
            )
        label   = ll_label(ll)
        passed  = ll >= LL_PASS
        result  = {
            "idx": st["current_idx"], "korean": phrase["korean"],
            "german": phrase["german"], "ll": ll, "passed": passed, "label": label,
        }
        new_state   = {**st, "pending_score": False, "results": st["results"] + [result]}
        highlighted = highlight_phrase(phrase)
        html = f"""
<div style="text-align:center;padding:20px 0">
  <div style="font-size:1.8em;margin-bottom:14px">{label}</div>
  <div style="font-size:1.25em;margin-bottom:10px"><b>Log-Likelihood: {ll:.4f}</b></div>
  <div style="font-size:1.35em">정답: <span style="font-style:italic">{highlighted}</span></div>
</div>"""
        return (gr.update(value=html), gr.update(interactive=True), new_state)

    def on_score_if_pending(audio, st):
        if not st.get("pending_score") or audio is None:
            return gr.update(), gr.update(), st
        return _do_score(audio, st)

    def on_mark_pending(st):
        return {**st, "pending_score": True}

    def on_next(st):
        new_idx = st["current_idx"] + 1
        n       = st["n_questions"]

        if new_idx >= n:
            results = st["results"]
            passed  = sum(1 for r in results if r["passed"])
            avg_ll  = sum(r["ll"] for r in results) / len(results) if results else 0
            rows    = "\n".join(
                f"| {r['idx']+1} | {r['korean']} | {r['german']} "
                f"| {r['ll']:.4f} | {r['label']} |"
                for r in results
            )
            summary = (
                f"## 🎉 {passed} / {n} 통과  (평균 Log-Likelihood: {avg_ll:.4f})\n\n"
                f"| # | 한국어 | 독일어 정답 | Log-Likelihood | 결과 |\n"
                f"|---|--------|-----------|----------------|------|\n"
                f"{rows}"
            )
            return (
                {**st, "current_idx": new_idx},
                gr.update(visible=False),             # setup_col
                gr.update(visible=True),              # quiz_col (유지)
                gr.update(value=""),                  # progress_md (clear)
                gr.update(value=""),                  # korean_md (clear)
                gr.update(value=""),                  # hint_md
                gr.update(interactive=False),          # hint_btn      (CSS로 숨김)
                gr.update(interactive=False),          # go_record_btn (CSS로 숨김)
                gr.update(visible=False, value=None),  # audio_input   (명시적 숨김)
                gr.update(interactive=False),          # score_btn     (CSS로 숨김)
                gr.update(value=""),                   # score_box
                gr.update(interactive=False),          # next_btn      (CSS로 숨김)
                summary,                               # result_md
                gr.update(interactive=True),           # restart_btn   (CSS로 표시)
            )

        phrase    = st["phrases"][new_idx]
        new_state = {**st, "current_idx": new_idx, "hint_text": ""}
        return _to_question(new_state, n, new_idx, phrase)

    def on_restart(_state):
        return (
            dict(INIT_STATE),
            gr.update(visible=True),    # setup_col
            gr.update(visible=False),   # quiz_col
        )

    # ── 이벤트 연결 ────────────────────────────────────────────────────────────

    def show_adj_grammar():
        return (
            gr.update(visible=True),   # grammar_hint_md
            gr.update(visible=True),   # adj_gallery
            gr.update(visible=True),   # adj_pdf_file
            gr.update(visible=False),  # noun_gallery
            gr.update(visible=False),  # noun_pdf_file
        )

    def show_noun_grammar():
        return (
            gr.update(visible=True),   # grammar_hint_md
            gr.update(visible=False),  # adj_gallery
            gr.update(visible=False),  # adj_pdf_file
            gr.update(visible=True),   # noun_gallery
            gr.update(visible=True),   # noun_pdf_file
        )

    GRAMMAR_TOGGLE_OUTS = [
        grammar_hint_md, adj_gallery, adj_pdf_file, noun_gallery, noun_pdf_file,
    ]
    adj_grammar_btn.click(show_adj_grammar, outputs=GRAMMAR_TOGGLE_OUTS)
    noun_grammar_btn.click(show_noun_grammar, outputs=GRAMMAR_TOGGLE_OUTS)

    start_btn.click(on_start, inputs=[n_radio, state], outputs=QUIZ_OUTS)

    hint_btn.click(on_hint, inputs=[state], outputs=[hint_md, state])

    go_record_btn.click(
        on_go_record,
        inputs=[state],
        outputs=[go_record_btn, hint_btn, audio_input, score_btn,
                 hint_md, score_box, next_btn],
    ).then(
        fn=None,
        js="""() => {
            setTimeout(() => {
                const btn = document.querySelector('.record-button')
                         || document.querySelector('button[aria-label="Record"]')
                         || document.querySelector('button.record');
                if (btn) btn.click();
            }, 800);
        }""",
    )

    score_btn.click(
        fn=on_mark_pending,
        inputs=[state],
        outputs=[state],
        js="() => { const s = document.querySelector('.stop-button'); if (s && getComputedStyle(s).display !== 'none') s.click(); }",
    ).then(
        fn=on_score_if_pending,
        inputs=[audio_input, state],
        outputs=[score_box, next_btn, state],
    )

    audio_input.stop_recording(
        fn=on_score_if_pending,
        inputs=[audio_input, state],
        outputs=[score_box, next_btn, state],
    )

    next_btn.click(on_next, inputs=[state], outputs=QUIZ_OUTS)

    restart_btn.click(
        on_restart,
        inputs=[state],
        outputs=[state, setup_col, quiz_col],
    )


if __name__ == "__main__":
    demo.launch(css=CSS, theme=gr.themes.Soft(), ssr_mode=False)
