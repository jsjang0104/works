import importlib
import json
import subprocess
from pathlib import Path

import pytest


def subject():
    assert importlib.util.find_spec("local_llm"), "Implement GPU eligibility and local fallback"
    return importlib.import_module("local_llm")


def test_busy_or_hidden_gpus_are_not_used():
    llm = subject()
    idle = llm.Gpu(0, "GPU-a", 30000, 0)
    busy = llm.Gpu(1, "GPU-b", 30000, 99)
    assert llm.choose_gpus([idle, busy], {"GPU-a"}, None, 24000) == []
    assert llm.choose_gpus([idle], set(), "", 24000) == []
    assert llm.choose_gpus([idle], set(), "-1", 24000) == []
    assert llm.choose_gpus([idle], set(), "1", 24000) == []


def test_memory_and_uuid_visibility_are_respected():
    llm = subject()
    small = llm.Gpu(0, "GPU-small", 12000, 0)
    large = llm.Gpu(1, "GPU-large", 30000, 0)
    assert llm.choose_gpus([small, large], set(), "GPU-large", 24000) == [large]
    assert llm.choose_gpus([small, large], set(), "0", 24000) == []


def test_missing_shard_is_rejected_before_loading(tmp_path):
    llm = subject()
    (tmp_path / "config.json").write_text("{}")
    (tmp_path / "tokenizer.json").write_text("{}")
    (tmp_path / "model.safetensors.index.json").write_text(
        json.dumps({"weight_map": {"weight": "missing.safetensors"}})
    )
    with pytest.raises(llm.LocalLLMUnavailable, match="가중치"):
        llm.validate_snapshot(tmp_path)


def test_sentences_parse_bilingual_json_and_reject_incomplete_output():
    llm = subject()
    pairs = [
        {"german": "Ich übe täglich.", "korean": "나는 매일 연습한다."},
        {"german": "Wir helfen einander.", "korean": "우리는 서로 돕는다."},
    ]
    assert llm.parse_sentences("```json\n" + json.dumps(pairs) + "\n```") == pairs
    invalid = [
        "not json",
        '["Ich übe.", "Wir helfen."]',
        json.dumps(pairs[:1]),
        json.dumps([{"german": "Hallo.", "korean": ""}] * 2),
        json.dumps([{"german": "Hallo."}] * 2),
        json.dumps([{"german": "Hallo.", "korean": "Hello."}] * 2),
        json.dumps([{"german": "x" * 401, "korean": "안녕"}] * 2),
    ]
    for text in invalid:
        with pytest.raises(llm.LocalLLMUnavailable):
            llm.parse_sentences(text)


def test_worker_timeout_becomes_manual_fallback(monkeypatch, tmp_path):
    llm = subject()
    monkeypatch.setattr(llm, "find_model_path", lambda: tmp_path)
    monkeypatch.setattr(llm, "available_gpus", lambda: [llm.Gpu(1, "GPU-free", 30000, 0)])

    def timeout(*args, **kwargs):
        assert kwargs["env"]["CUDA_VISIBLE_DEVICES"] == "GPU-free"
        assert kwargs["timeout"] > 0
        raise subprocess.TimeoutExpired(args[0], kwargs["timeout"])

    monkeypatch.setattr(llm.subprocess, "run", timeout)
    with pytest.raises(llm.LocalLLMUnavailable, match="시간"):
        llm.generate_sentences(["Haus", "Baum"])


def test_worker_failure_is_not_mistaken_for_sentences(monkeypatch, tmp_path):
    llm = subject()
    monkeypatch.setattr(llm, "find_model_path", lambda: tmp_path)
    monkeypatch.setattr(llm, "available_gpus", lambda: [llm.Gpu(0, "GPU-free", 30000, 0)])
    monkeypatch.setattr(
        llm.subprocess,
        "run",
        lambda *a, **k: subprocess.CompletedProcess(a[0], 1, "", "out of memory"),
    )
    with pytest.raises(llm.LocalLLMUnavailable):
        llm.generate_sentences(["Haus", "Baum"])


def test_no_gpu_does_not_start_worker(monkeypatch):
    llm = subject()

    def unavailable():
        raise llm.LocalLLMUnavailable("사용 가능한 GPU가 없습니다.")

    monkeypatch.setattr(llm, "available_gpus", unavailable)
    monkeypatch.setattr(llm, "find_model_path", lambda: Path("/cache/model"))
    with pytest.raises(llm.LocalLLMUnavailable, match="GPU"):
        llm.generate_sentences(["Haus", "Baum"])


def test_worker_returns_both_languages_without_losing_translation(monkeypatch, tmp_path):
    llm = subject()
    pairs = [
        {"german": "Ich übe täglich.", "korean": "나는 매일 연습한다."},
        {"german": "Wir helfen einander.", "korean": "우리는 서로 돕는다."},
    ]
    monkeypatch.setattr(llm, "find_model_path", lambda: tmp_path)
    monkeypatch.setattr(llm, "available_gpus", lambda: [llm.Gpu(0, "GPU-free", 30000, 0)])
    monkeypatch.setattr(
        llm.subprocess,
        "run",
        lambda *a, **k: subprocess.CompletedProcess(a[0], 0, json.dumps(pairs), ""),
    )
    assert llm.generate_sentences(["üben", "helfen"]) == pairs


def test_idle_4090s_are_selected_together_with_the_default_memory_budget():
    import settings

    llm = subject()
    gpus = [llm.Gpu(index, f"GPU-{index}", 24078, 0) for index in range(4)]
    assert (
        llm.choose_gpus(
            gpus, set(), None, settings.MIN_FREE_GPU_MIB, settings.GPU_MEMORY_RESERVE_MIB
        )
        == gpus
    )


def test_multiple_gpus_pool_memory_after_reserving_inference_space():
    llm = subject()
    gpus = [llm.Gpu(1, "GPU-a", 12288, 0), llm.Gpu(3, "GPU-b", 12288, 0)]
    assert llm.choose_gpus(gpus, set(), "1,3", 20480, 2048) == gpus
    assert llm.choose_gpus(gpus, set(), "GPU-a,GPU-b", 20480, 2048) == gpus
    assert llm.choose_gpus(gpus, set(), None, 20481, 2048) == []
    assert llm.choose_gpus(gpus, {"GPU-b"}, None, 20480, 2048) == []
    assert llm.choose_gpus(gpus, set(), "3", 20480, 2048) == []


def test_memory_budget_uses_local_device_ids_and_keeps_inference_headroom(monkeypatch):
    llm = subject()
    monkeypatch.setattr(llm.settings, "MIN_FREE_GPU_MIB", 20480)
    monkeypatch.setattr(llm.settings, "GPU_MEMORY_RESERVE_MIB", 2048)
    assert llm.gpu_memory_budget([12 * 1024**3, 14 * 1024**3]) == {
        0: 10 * 1024**3,
        1: 12 * 1024**3,
        "cpu": 0,
    }
    with pytest.raises(llm.LocalLLMUnavailable, match="메모리"):
        llm.gpu_memory_budget([12 * 1024**3])


def test_worker_receives_every_selected_gpu_uuid(monkeypatch, tmp_path):
    llm = subject()
    pairs = [
        {"german": "Ich übe täglich.", "korean": "나는 매일 연습한다."},
        {"german": "Wir helfen einander.", "korean": "우리는 서로 돕는다."},
    ]
    monkeypatch.setattr(llm, "find_model_path", lambda: tmp_path)
    monkeypatch.setattr(
        llm,
        "available_gpus",
        lambda: [llm.Gpu(1, "GPU-a", 24078, 0), llm.Gpu(3, "GPU-b", 24078, 0)],
    )

    def run_worker(*args, **kwargs):
        assert kwargs["env"]["CUDA_VISIBLE_DEVICES"] == "GPU-a,GPU-b"
        return subprocess.CompletedProcess(args[0], 0, json.dumps(pairs), "")

    monkeypatch.setattr(llm.subprocess, "run", run_worker)
    assert llm.generate_sentences(["üben", "helfen"]) == pairs
