"""
LLM-as-a-judge QE scoring using Qwen3-32B (transformers local) for klook_data.json

ref가 있는 항목의 tgt에 대해 0~100 점수를 계산하고 /100으로 정규화하여
BLEURT·COMETKiwi와 동일한 0~1 범위로 "Qwen3-32B" 필드를 업데이트합니다.

Requirements:
    pip install transformers accelerate
"""

import json
import torch
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForCausalLM

INPUT_PATH  = Path(__file__).parent / "klook_data.json"
OUTPUT_PATH = Path(__file__).parent / "klook_data.json"

MODEL_NAME = "Qwen/Qwen3-32B"

PROMPT_TEMPLATE = (
    "Score the following translation from English to Korean on a scale from 0 to 100, "
    "where a score of 0 means a broken or poor translation; 33 indicates a flawed "
    "translation with significant issues; 66 indicates a good translation with only "
    "minor issues in grammar, fluency, or consistency; and 100 represents a perfect "
    "translation in both meaning and grammar. Answer with only a whole number "
    "representing the score, and nothing else.\n\n"
    "English source text:\n{source_seg}\n\n"
    "Korean translation:\n{target_seg}"
)


def main():
    with open(INPUT_PATH, encoding="utf-8") as f:
        data = json.load(f)

    targets = [
        (i, entry) for i, entry in enumerate(data)
        if entry.get("ref") and entry.get("tgt") and entry.get("Qwen3-32B") is None
    ]
    print(f"Loaded {len(data)} entries, {len(targets)} have ref+tgt → scoring these")
    print(f"Model: {MODEL_NAME}\n")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        dtype=torch.bfloat16,
        device_map="auto",  # 2x GPU에 자동 분산
    )
    model.eval()

    for n, (idx, entry) in enumerate(targets, 1):
        prompt = PROMPT_TEMPLATE.format(source_seg=entry["src"], target_seg=entry["tgt"])
        messages = [{"role": "user", "content": prompt}]
        text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True, enable_thinking=False)

        inputs = tokenizer(text, return_tensors="pt").to(model.device)
        with torch.no_grad():
            output_ids = model.generate(
                **inputs,
                max_new_tokens=10,
                do_sample=False,
                pad_token_id=tokenizer.eos_token_id,
            )

        generated = output_ids[0][inputs["input_ids"].shape[1]:]
        raw_text = tokenizer.decode(generated, skip_special_tokens=True).strip()
        raw = int(raw_text)
        score = round(raw / 100, 4)  # 0~100 → 0~1 (BLEURT·COMETKiwi와 동일 범위)

        data[idx]["Qwen3-32B"] = score
        print(f"[{n:2d}/{len(targets)}] {entry['src'][:55]!r:58s} → {score:.4f}")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\nSaved → {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
