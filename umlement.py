#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CLI entry point and orchestration layer for local UMLement runs."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from colorama import Fore, Style, deinit, init

from constants import OUTPUT_DIR, SUPPORTED_OUTPUT_FORMATS
from progress_types import ProgressSink
from uml_generator import UMLGenerator
from umlement_progress import ProgressReporter


class UMLement:
    """Coordinate input validation plus model and diagram generation work."""

    def __init__(
        self,
        progress_enabled: bool = False,
        progress: ProgressSink | None = None,
        show_accessors: bool = False,
    ) -> None:
        self.progress: ProgressSink = progress or ProgressReporter(enabled=progress_enabled)
        self.generator: UMLGenerator = UMLGenerator(progress=self.progress, show_accessors=show_accessors)

    def generate_class_inheritance_model(self) -> Path:
        """Generate the PlantUML model artifact for the current run."""
        return self.generator.generate_class_inheritance_model()

    def generate_class_inheritance_diagram(self, output_format: str = "png") -> Path:
        """Render the current PlantUML model into a diagram artifact."""
        return self.generator.generate_class_inheritance_diagram(output_format=output_format)

    def _append_python_path(self, path: Path) -> None:
        """Queue one supported Python file path for downstream model generation."""
        if path.is_file() and path.suffix.lower() == ".py":
            resolved = str(path.resolve())
            if resolved not in self.generator.py_files:
                self.generator.py_files.append(resolved)
                self.progress.info("Queued Python file", resolved)
            return

        self.progress.info("Ignored unsupported path", str(path))
        print(rf"{Fore.LIGHTBLACK_EX}{path} ignored, non-python files are unsupported{Style.RESET_ALL}")

    def validate_argvs_provided(self, argvs_provided: list[str], recursive: bool = False) -> bool:
        """Validate CLI-style input paths and expand directories into Python file lists."""
        min_argvs_required: int = 1

        if len(argvs_provided) < min_argvs_required:
            print(
                f"{Fore.RED}an insufficient # of script arguments were provided "
                f"(provided: {len(argvs_provided)}, expected: {min_argvs_required}){Style.RESET_ALL}"
            )
            return False

        self.progress.start("Validating input paths")
        self.generator.py_files = []

        for argv in argvs_provided:
            path = Path(argv).expanduser()

            if not path.exists():
                self.progress.info("Missing path", str(path))
                print(f"{Fore.RED}{path} not found{Style.RESET_ALL}")
                continue

            if path.is_dir():
                mode = "recursive" if recursive else "top-level"
                self.progress.info("Scanning directory", f"{path} ({mode})")
                iterator = sorted(path.rglob("*.py") if recursive else path.iterdir())
                for file_path in iterator:
                    self._append_python_path(file_path)
                continue

            self._append_python_path(path)

        if len(self.generator.py_files) < 1:
            print(f"{Fore.RED}no .py files found{Style.RESET_ALL}")
            return False

        self.progress.complete("Input validation complete", f"{len(self.generator.py_files)} Python file(s) ready")
        return True


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser for local UMLement execution."""
    parser = argparse.ArgumentParser(
        description="Generate PlantUML class diagrams from Python source files.",
    )
    parser.add_argument("paths", nargs="+", help="Python files or folders to scan")
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Recursively scan folders for Python files",
    )
    parser.add_argument(
        "-f",
        "--format",
        default="png",
        choices=SUPPORTED_OUTPUT_FORMATS,
        help="Diagram output format",
    )
    parser.add_argument(
        "--model-only",
        action="store_true",
        help="Generate the PlantUML model without rendering an image",
    )
    parser.add_argument(
        "--progress",
        action="store_true",
        help="Show step-by-step status output while running",
    )
    parser.add_argument(
        "--show-accessors",
        action="store_true",
        help="Include getter and setter methods in generated UML members",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="UMLement 0.2.0",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the UMLement CLI and return a shell-friendly exit status code."""
    args = build_parser().parse_args(argv)
    init()

    try:
        script = UMLement(progress_enabled=args.progress, show_accessors=args.show_accessors)
        argvs_validated = script.validate_argvs_provided(args.paths, recursive=args.recursive)

        if not argvs_validated:
            raise ValueError("input validation failed")

        script.progress.advance("Generating PlantUML model")
        model_path = script.generate_class_inheritance_model()
        print(f"{Fore.CYAN}PlantUML model created: {model_path}{Style.RESET_ALL}")

        if args.model_only:
            script.progress.complete("Run complete", "model-only execution")
            print(f"{Fore.GREEN}model generation complete, diagram rendering skipped{Style.RESET_ALL}")
            return 0

        diagram_path = script.generate_class_inheritance_diagram(output_format=args.format)
        script.progress.complete("Run complete", f"diagram available at {diagram_path}")
        print(f"{Fore.GREEN}diagram created successfully: {diagram_path}{Style.RESET_ALL}")
        return 0

    except Exception as exc:
        print(f"{Fore.RED}class inheritance model & diagram creation failed: {exc}{Style.RESET_ALL}")
        output_dir = Path(OUTPUT_DIR)
        if output_dir.exists():
            shutil.rmtree(output_dir)
        return 1
    finally:
        deinit()


if __name__ == "__main__":
    sys.exit(main())
