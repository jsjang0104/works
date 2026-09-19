"""Use an idle local GPU, with all heavyweight inference isolated in a child process."""

import contextlib
import csv
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import settings


class LocalLLMUnavailable(RuntimeError):
    pass


@dataclass(frozen=True)
class Gpu:
    index: int
    uuid: str
    free_mib: int
    utilization: int


def choose_gpu(
    gpus: list[Gpu], occupied: set[str], visible: str | None, required_mib: int
) -> Gpu | None:
    allowed = (
        None if visible is None else {part.strip() for part in visible.split(",") if part.strip()}
    )
    candidates = []
    for gpu in gpus:
        if allowed is not None and not any(
            value == str(gpu.index) or (value.startswith("GPU-") and gpu.uuid.startswith(value))
            for value in allowed
        ):
            continue
        if gpu.uuid not in occupied and gpu.free_mib >= required_mib and gpu.utilization <= 10:
            candidates.append(gpu)
    return max(candidates, key=lambda gpu: gpu.free_mib, default=None)


def available_gpu() -> Gpu:
    try:
        summary = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=index,uuid,memory.free,utilization.gpu",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )
        processes = subprocess.run(
            ["nvidia-smi", "--query-compute-apps=gpu_uuid", "--format=csv,noheader,nounits"],
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )
        gpus = [
            Gpu(int(index), uuid.strip(), int(free), int(util))
            for index, uuid, free, util in csv.reader(summary.stdout.splitlines())
        ]
        occupied = {line.strip() for line in processes.stdout.splitlines() if line.strip()}
    except (OSError, subprocess.SubprocessError, ValueError) as error:
        raise LocalLLMUnavailable("GPU 상태를 확인할 수 없습니다.") from error
    gpu = choose_gpu(
        gpus, occupied, os.environ.get("CUDA_VISIBLE_DEVICES"), settings.MIN_FREE_GPU_MIB
    )
    if gpu is None:
        raise LocalLLMUnavailable("사용 가능한 GPU가 없거나 여유 메모리가 부족합니다.")
    return gpu


def validate_snapshot(path: Path) -> Path:
    if not (path / "config.json").is_file() or not (path / "tokenizer.json").is_file():
        raise LocalLLMUnavailable("로컬 모델 설정 또는 토크나이저 캐시가 없습니다.")
    try:
        index_path = path / "model.safetensors.index.json"
        if index_path.is_file():
            index = json.loads(index_path.read_text())
            shards = set(index["weight_map"].values())
        else:
            shards = {"model.safetensors"}
        if not shards or any(not (path / shard).is_file() for shard in shards):
            raise ValueError("Missing shards")
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise LocalLLMUnavailable("로컬 모델 가중치 캐시가 없거나 불완전합니다.") from error
    return path


def find_model_path() -> Path:
    if settings.MODEL_PATH is not None:
        return validate_snapshot(Path(settings.MODEL_PATH).expanduser())
    if os.environ.get("HF_HUB_CACHE"):
        roots = [Path(os.environ["HF_HUB_CACHE"])]
    else:
        roots = [
            Path(os.environ.get("HF_HOME", str(settings.SHARED_HF_HOME))) / "hub",
            Path.home() / ".cache/huggingface/hub",
        ]
    cache_name = "models--" + settings.MODEL_ID.replace("/", "--")
    for root in roots:
        repo = root / cache_name
        snapshots = repo / "snapshots"
        if not snapshots.is_dir():
            continue
        candidates = sorted(
            snapshots.iterdir(), key=lambda path: path.stat().st_mtime, reverse=True
        )
        ref = repo / "refs/main"
        if ref.is_file():
            current = snapshots / ref.read_text().strip()
            candidates = [current] + [path for path in candidates if path != current]
        for path in candidates:
            try:
                return validate_snapshot(path)
            except LocalLLMUnavailable:
                continue
    raise LocalLLMUnavailable(
        "사용 가능한 Gemma 캐시를 찾지 못했습니다. settings.py의 MODEL_PATH를 확인하세요."
    )


def parse_sentences(text: str) -> list[dict[str, str]]:
    value = text.strip()
    if value.startswith("```"):
        value = "\n".join(value.splitlines()[1:])
        value = value.removesuffix("```").strip()
    try:
        sentences = json.loads(value)
        if isinstance(sentences, dict):
            sentences = sentences.get("sentences")
        if not isinstance(sentences, list) or len(sentences) != 2:
            raise ValueError("Expected two sentences")
        pairs = []
        for pair in sentences:
            if not isinstance(pair, dict):
                raise TypeError("Expected German/Korean pair")
            if any(
                not isinstance(pair.get(key), str) or not pair[key].strip() or len(pair[key]) > 400
                for key in ("german", "korean")
            ):
                raise ValueError("Missing or invalid German/Korean text")
            if not re.search(r"[가-힣]", pair["korean"]):
                raise ValueError("Expected Korean translation")
            pairs.append({key: " ".join(pair[key].split()) for key in ("german", "korean")})
        return pairs
    except (ValueError, TypeError) as error:
        raise LocalLLMUnavailable(
            "모델에서 사용할 수 있는 독일어 문장과 한국어 해석 두 쌍을 얻지 못했습니다."
        ) from error


def generate_sentences(words: list[str]) -> list[dict[str, str]]:
    gpu = available_gpu()
    path = find_model_path()
    environment = os.environ.copy()
    environment["CUDA_VISIBLE_DEVICES"] = gpu.uuid
    environment["TOKENIZERS_PARALLELISM"] = "false"
    # The subprocess makes failure/timeout release all model allocations before manual input.
    try:
        result = subprocess.run(
            [sys.executable, str(Path(__file__).resolve()), "--worker", str(path)],
            input=json.dumps(words, ensure_ascii=False),
            capture_output=True,
            text=True,
            env=environment,
            timeout=settings.LLM_TIMEOUT_SECONDS,
            check=False,
        )
    except subprocess.TimeoutExpired as error:
        raise LocalLLMUnavailable("로컬 모델의 응답 시간이 초과되었습니다.") from error
    except OSError as error:
        raise LocalLLMUnavailable("로컬 모델 실행 환경을 시작할 수 없습니다.") from error
    if result.returncode != 0:
        raise LocalLLMUnavailable(
            "로컬 모델 로딩·추론에 실패했습니다. GPU와 requirements-local.txt를 확인하세요."
        )
    return parse_sentences(result.stdout)


def _worker(path: Path, words: list[str]) -> list[dict[str, str]]:
    # Check again before importing torch; a previously idle GPU may now be occupied.
    available_gpu()
    import torch
    from transformers import AutoTokenizer, BitsAndBytesConfig, Gemma4ForConditionalGeneration

    if not torch.cuda.is_available():
        raise LocalLLMUnavailable("CUDA unavailable")
    free_bytes, _ = torch.cuda.mem_get_info(0)
    if free_bytes < settings.MIN_FREE_GPU_MIB * 1024**2:
        raise LocalLLMUnavailable("Insufficient GPU memory")
    quantization = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.bfloat16,
    )
    tokenizer = AutoTokenizer.from_pretrained(path, local_files_only=True)
    model = Gemma4ForConditionalGeneration.from_pretrained(
        path,
        local_files_only=True,
        device_map={"": 0},
        dtype=torch.bfloat16,
        quantization_config=quantization,
        attn_implementation="sdpa",
    )
    model.eval()
    prompt = (
        "Write one natural German sentence at CEFR B1–B2 level for EACH word below, "
        "in the same order. Each sentence must use its assigned word (inflection is allowed), "
        "describe an everyday situation, and contain about 12–25 words. "
        "For each sentence, provide an accurate, natural Korean translation using Hangul. "
        "Return ONLY a JSON array of two objects with keys german and korean, "
        'like [{"german":"...", "korean":"..."}, {"german":"...", "korean":"..."}]. '
        "Keep each German sentence and Korean translation under 400 characters. "
        "No explanations, markdown, or extra keys. "
        "Words: " + json.dumps(words, ensure_ascii=False)
    )
    inputs = tokenizer.apply_chat_template(
        [{"role": "user", "content": prompt}],
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
        enable_thinking=False,
    )
    inputs = {name: tensor.to("cuda:0") for name, tensor in inputs.items()}
    input_length = inputs["input_ids"].shape[-1]
    with torch.inference_mode():
        result = model.generate(**inputs, max_new_tokens=768, do_sample=False)
    return parse_sentences(tokenizer.decode(result[0, input_length:], skip_special_tokens=True))


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] != "--worker":
        raise SystemExit("Run main.py to use the terminal interface.")
    try:
        words = json.load(sys.stdin)
        with contextlib.redirect_stdout(sys.stderr):
            sentences = _worker(Path(sys.argv[2]), words)
        print(json.dumps(sentences, ensure_ascii=False))
    except Exception as error:  # noqa: BLE001 -- worker failures must become manual input
        print(type(error).__name__, file=sys.stderr)
        raise SystemExit(1)
