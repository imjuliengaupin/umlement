from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from umlement_runner import run_umlement


def test_run_umlement_model_only_returns_model_path(tmp_path: Path) -> None:
    source_file = tmp_path / "sample.py"
    source_file.write_text("class Demo(object):\n    pass\n", encoding="utf-8")

    events: list[tuple[str, str | None]] = []

    result = run_umlement([str(source_file)], model_only=True, progress_callback=lambda label, detail: events.append((label, detail)))

    assert result.success is True
    assert result.model_path is not None
    assert result.diagram_path is None
    assert any("Run complete" in label for label, _ in events)
