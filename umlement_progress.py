from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter

from colorama import Fore, Style


@dataclass
class ProgressEvent:
    label: str
    detail: str | None = None


class ProgressReporter:
    def __init__(self, enabled: bool = True) -> None:
        self.enabled = enabled
        self._started_at = perf_counter()
        self._step = 0

    def start(self, label: str, detail: str | None = None) -> None:
        self._emit("▶", Fore.CYAN, label, detail)

    def advance(self, label: str, detail: str | None = None) -> None:
        self._step += 1
        self._emit(f"{self._step}.", Fore.BLUE, label, detail)

    def complete(self, label: str, detail: str | None = None) -> None:
        elapsed = perf_counter() - self._started_at
        suffix = f" ({elapsed:.2f}s elapsed)"
        merged_detail = f"{detail}{suffix}" if detail else suffix.strip()
        self._emit("✓", Fore.GREEN, label, merged_detail)

    def info(self, label: str, detail: str | None = None) -> None:
        self._emit("•", Fore.LIGHTBLACK_EX, label, detail)

    def _emit(self, prefix: str, color: str, label: str, detail: str | None) -> None:
        if not self.enabled:
            return
        message = f"{color}{prefix} {label}{Style.RESET_ALL}"
        if detail:
            message += f"\n   {Fore.LIGHTBLACK_EX}{detail}{Style.RESET_ALL}"
        print(message)
