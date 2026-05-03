from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
from typing import Callable

from constants import OUTPUT_DIR
from umlement import UMLement


ProgressCallback = Callable[[str, str | None], None]


@dataclass
class RunResult:
    success: bool
    model_path: str | None = None
    diagram_path: str | None = None
    error: str | None = None


class CallbackProgressReporter:
    def __init__(self, callback: ProgressCallback | None = None) -> None:
        self.callback = callback

    def start(self, label: str, detail: str | None = None) -> None:
        self._emit("start", label, detail)

    def advance(self, label: str, detail: str | None = None) -> None:
        self._emit("advance", label, detail)

    def complete(self, label: str, detail: str | None = None) -> None:
        self._emit("complete", label, detail)

    def info(self, label: str, detail: str | None = None) -> None:
        self._emit("info", label, detail)

    def _emit(self, kind: str, label: str, detail: str | None = None) -> None:
        if self.callback:
            rendered = f"[{kind}] {label}"
            self.callback(rendered, detail)


def run_umlement(paths: list[str], recursive: bool = False, output_format: str = "svg", model_only: bool = False, progress_callback: ProgressCallback | None = None) -> RunResult:
    progress = CallbackProgressReporter(progress_callback)
    script = UMLement(progress_enabled=False)
    script.progress = progress
    script.generator.progress = progress

    try:
        argvs_validated = script.validate_argvs_provided(paths, recursive=recursive)
        if not argvs_validated:
            raise ValueError("input validation failed")

        progress.advance("Generating PlantUML model")
        model_path = script.generate_class_inheritance_model()

        if model_only:
            progress.complete("Run complete", "model-only execution")
            return RunResult(success=True, model_path=str(model_path))

        diagram_path = script.generate_class_inheritance_diagram(output_format=output_format)
        progress.complete("Run complete", f"diagram available at {diagram_path}")
        return RunResult(success=True, model_path=str(model_path), diagram_path=str(diagram_path))

    except Exception as exc:
        output_dir = Path(OUTPUT_DIR)
        if output_dir.exists():
            shutil.rmtree(output_dir)
        return RunResult(success=False, error=str(exc))
