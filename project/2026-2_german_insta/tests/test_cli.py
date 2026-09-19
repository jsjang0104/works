import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

from PIL import Image


def test_cli_uses_project_date_directory_when_launched_elsewhere(tmp_path):
    source = Path(__file__).resolve().parents[1]
    project = tmp_path / "2026-2_german_insta"
    project.mkdir()
    for name in ("main.py", "settings.py", "cards.py"):
        shutil.copy(source / name, project / name)
    shutil.copytree(source / "fonts", project / "fonts")
    image = tmp_path / "input.png"
    Image.new("RGB", (200, 200), "goldenrod").save(image)
    command = [sys.executable, str(project / "main.py")]
    # No model/MCP modules are copied: exercise the real manual/recovery paths offline.
    user_input = (
        "groß\nhelfen\nDer Garten ist groß.\n그 정원은 크다.\n"
        f"Wir helfen einander.\n우리는 서로 돕는다.\n{image}\n{image}\n"
    )
    day_before = datetime.now(UTC).astimezone().date().isoformat()
    first = subprocess.run(
        command,
        input=user_input,
        capture_output=True,
        text=True,
        cwd=tmp_path,
        check=False,
    )
    day_after = datetime.now(UTC).astimezone().date().isoformat()
    assert first.returncode == 0, first.stdout + first.stderr
    assert "직접 독일어 문장을 입력해라" in first.stdout
    assert "기존 이미지 파일 경로" in first.stdout
    outputs = list(project.glob("20??-??-??"))
    assert len(outputs) == 1
    assert outputs[0].name in (day_before, day_after)
    assert not (tmp_path / outputs[0].name).exists()
    initial = {path.name: path.read_bytes() for path in outputs[0].iterdir()}
    second = subprocess.run(
        command,
        input=user_input,
        capture_output=True,
        text=True,
        cwd=tmp_path,
        check=False,
    )
    assert second.returncode == 0, second.stdout + second.stderr
    assert len(list(outputs[0].glob("*.jpg"))) == 4
    assert len(list(outputs[0].glob("*.txt"))) == 4
    assert all(
        (outputs[0] / name).read_bytes() == content for name, content in initial.items()
    )
