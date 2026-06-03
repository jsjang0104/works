import gradio as gr
import sys
import os
import re
import torch

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, "grammar"))
from declension import generate_phrase

# ── Whisper ───────────────────────────────────────────────────────────────────
import whisper

_device = "cuda" if torch.cuda.is_available() else "cpu"
_model  = whisper.load_model("tiny", device=_device)
# fine-tuning 완료 후 아래로 교체:
# _model = whisper.load_model("/path/to/finetuned_tiny_model", device=_device)


def transcribe(audio_path: str) -> str:
    if not audio_path:
        return ""
    result = _model.transcribe(audio_path, language="de", fp16=(_device == "cuda"))
    return result["text"].strip()


def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\säöüß]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def hint_str(hint: list) -> str:
    return "  ·  ".join(f"`{w}`" for w in hint)


# ── 이벤트 핸들러 ──────────────────────────────────────────────────────────────

def start(n: int):
    qs = [generate_phrase() for _ in range(n)]
    q  = qs[0]
    return (
        qs,                                          # state_qs
        0,                                           # state_idx
        0,                                           # state_score
        gr.update(visible=False),                    # setup_col
        gr.update(visible=True),                     # quiz_col
        gr.update(visible=False),                    # result_col
        "",                                          # final_md
        f"**1 / {n}**",                              # progress_md
        f"## {q['korean']}",                         # korean_md
        hint_str(q['hint']),                         # hint_md
        None,                                        # audio_in (reset)
        "",                                          # text_in (reset)
        gr.update(value="", visible=False),          # result_md
        gr.update(visible=False),                    # next_btn
    )


def submit(audio, text, questions, idx, score):
    q = questions[idx]

    if audio:
        user_ans = transcribe(audio)
    elif text.strip():
        user_ans = text.strip()
    else:
        return (
            score,
            gr.update(value="⚠️ 마이크로 말하거나 텍스트를 입력하세요.", visible=True),
            gr.update(visible=False),
        )

    correct   = normalize(user_ans) == normalize(q["german"])
    new_score = score + (1 if correct else 0)

    if correct:
        feedback = f"✅ **정답!**\n\n> {q['german']}"
    else:
        feedback = f"❌ **오답**\n\n내 답변: `{user_ans}`\n\n정답: **{q['german']}**"

    return (
        new_score,
        gr.update(value=feedback, visible=True),
        gr.update(visible=True),
    )


def next_question(questions, idx, score):
    new_idx = idx + 1
    n       = len(questions)

    if new_idx >= n:
        pct     = score / n * 100
        comment = (
            "🎉 완벽해요!"           if pct == 100 else
            "👍 잘했어요!"           if pct >= 80  else
            "😊 조금 더 연습해봐요!" if pct >= 60  else
            "📚 계속 연습하면 늘 거예요!"
        )
        final = f"# 결과\n\n**{score} / {n}** 정답 ({pct:.0f}점)\n\n{comment}"
        return (
            new_idx, score,
            gr.update(visible=False),               # quiz_col
            gr.update(visible=True),                # result_col
            final,
            "", "", "",                             # progress / korean / hint
            None, "",
            gr.update(value="", visible=False),
            gr.update(visible=False),
        )

    q = questions[new_idx]
    return (
        new_idx, score,
        gr.update(visible=True),                    # quiz_col
        gr.update(visible=False),                   # result_col
        "",
        f"**{new_idx + 1} / {n}**",
        f"## {q['korean']}",
        hint_str(q['hint']),
        None, "",
        gr.update(value="", visible=False),
        gr.update(visible=False),
    )


def restart():
    return (
        [], 0, 0,
        gr.update(visible=True),
        gr.update(visible=False),
        gr.update(visible=False),
    )


# ── UI ────────────────────────────────────────────────────────────────────────

with gr.Blocks(title="독일어 명사구 퀴즈", theme=gr.themes.Soft()) as demo:

    state_qs    = gr.State([])
    state_idx   = gr.State(0)
    state_score = gr.State(0)

    # ── Setup 화면 ──────────────────────────────────────────────────────────
    with gr.Column(visible=True) as setup_col:
        gr.Markdown("# 🇩🇪 독일어 명사구 퀴즈")
        gr.Markdown("격변화(Deklination) 연습 — 한국어를 보고 독일어로 말하거나 쓰세요.")
        gr.Markdown("### 몇 개 연습할까요?")
        with gr.Row():
            cnt_btns = [
                gr.Button(str(n), variant="primary", scale=1)
                for n in [10, 20, 30, 40, 50]
            ]

    # ── 퀴즈 화면 ──────────────────────────────────────────────────────────
    with gr.Column(visible=False) as quiz_col:
        progress_md = gr.Markdown("**1 / 10**")
        korean_md   = gr.Markdown("## ...")
        with gr.Accordion("💡 단어 힌트 (클릭하여 열기)", open=False):
            hint_md = gr.Markdown("...")
        with gr.Tabs():
            with gr.Tab("🎤 마이크"):
                audio_in = gr.Audio(
                    sources=["microphone"],
                    type="filepath",
                    label="독일어로 말하세요",
                )
            with gr.Tab("⌨️ 타이핑"):
                text_in = gr.Textbox(placeholder="독일어로 입력하세요...", label="")
        submit_btn = gr.Button("제출", variant="primary", size="lg")
        result_md  = gr.Markdown("", visible=False)
        next_btn   = gr.Button("다음 →", visible=False)

    # ── 결과 화면 ──────────────────────────────────────────────────────────
    with gr.Column(visible=False) as result_col:
        final_md    = gr.Markdown("")
        restart_btn = gr.Button("다시 시작", variant="primary")

    # ── 이벤트 연결 ─────────────────────────────────────────────────────────

    start_outs = [
        state_qs, state_idx, state_score,
        setup_col, quiz_col, result_col,
        final_md, progress_md, korean_md, hint_md,
        audio_in, text_in, result_md, next_btn,
    ]
    for btn, n in zip(cnt_btns, [10, 20, 30, 40, 50]):
        btn.click(fn=lambda n=n: start(n), inputs=[], outputs=start_outs)

    submit_btn.click(
        fn=submit,
        inputs=[audio_in, text_in, state_qs, state_idx, state_score],
        outputs=[state_score, result_md, next_btn],
    )

    next_outs = [
        state_idx, state_score,
        quiz_col, result_col, final_md,
        progress_md, korean_md, hint_md,
        audio_in, text_in, result_md, next_btn,
    ]
    next_btn.click(
        fn=next_question,
        inputs=[state_qs, state_idx, state_score],
        outputs=next_outs,
    )

    restart_btn.click(
        fn=restart,
        inputs=[],
        outputs=[state_qs, state_idx, state_score, setup_col, quiz_col, result_col],
    )

if __name__ == "__main__":
    demo.launch()
