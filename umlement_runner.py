from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Callable

from constants import OUTPUT_DIR
from umlement import UMLement

ProgressCallback = Callable[[str, str | None], None]


@dataclass
class RunResult:
    """Normalized result payload for CLI and UI-triggered UMLement runs."""

    success: bool
    model_path: str | None = None
    diagram_path: str | None = None
    error: str | None = None


class CallbackProgressReporter:
    """Adapter that converts runner lifecycle events into UI-friendly callbacks."""

    def __init__(self, callback: ProgressCallback | None = None) -> None:
        self.callback = callback
        self._started_at = perf_counter()
        self._step = 0

    def start(self, label: str, detail: str | None = None) -> None:
        """Emit a run-start event."""
        self._emit("start", label, detail)

    def advance(self, label: str, detail: str | None = None) -> None:
        """Emit an in-progress milestone update."""
        self._step += 1
        self._emit("advance", label, detail)

    def complete(self, label: str, detail: str | None = None) -> None:
        """Emit the terminal success event with elapsed runtime context."""
        elapsed = perf_counter() - self._started_at
        suffix = f"{elapsed:.2f}s elapsed"
        merged_detail = f"{detail} ({suffix})" if detail else suffix
        self._emit("complete", label, merged_detail)

    def info(self, label: str, detail: str | None = None) -> None:
        """Emit an informational event that should not be decorated as lifecycle state."""
        self._emit("info", label, detail)

    def _emit(self, kind: str, label: str, detail: str | None = None) -> None:
        """Render and forward a progress event when a callback is registered."""
        if self.callback:
            rendered = label if kind == "info" else f"[{kind}] {label}"
            self.callback(rendered, detail)


def run_umlement(
    paths: list[str],
    recursive: bool = False,
    output_format: str = "svg",
    model_only: bool = False,
    show_accessors: bool = False,
    progress_callback: ProgressCallback | None = None,
) -> RunResult:
    """Run UMLement against validated input paths and return generated artifact locations."""
    progress = CallbackProgressReporter(progress_callback)
    script = UMLement(progress_enabled=False, show_accessors=show_accessors)
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
