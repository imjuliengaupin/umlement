#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import sys

from colorama import Fore, Style, deinit, init

from constants import OUTPUT_DIR, SUPPORTED_OUTPUT_FORMATS
from uml_generator import UMLGenerator


class UMLement:
    def __init__(self) -> None:
        self.generator: UMLGenerator = UMLGenerator()

    def generate_class_inheritance_model(self) -> Path:
        return self.generator.generate_class_inheritance_model()

    def generate_class_inheritance_diagram(self, output_format: str = "png") -> Path:
        return self.generator.generate_class_inheritance_diagram(output_format=output_format)

    def _append_python_path(self, path: Path) -> None:
        if path.is_file() and path.suffix.lower() == ".py":
            resolved = str(path.resolve())
            if resolved not in self.generator.py_files:
                self.generator.py_files.append(resolved)
            return

        print(rf"{Fore.LIGHTBLACK_EX}{path} ignored, non-python files are unsupported{Style.RESET_ALL}")

    def validate_argvs_provided(self, argvs_provided: list[str], recursive: bool = False) -> bool:
        min_argvs_required: int = 1

        if len(argvs_provided) < min_argvs_required:
            print(
                f"{Fore.RED}an insufficient # of script arguments were provided "
                f"(provided: {len(argvs_provided)}, expected: {min_argvs_required}){Style.RESET_ALL}"
            )
            return False

        self.generator.py_files = []

        for argv in argvs_provided:
            path = Path(argv).expanduser()

            if not path.exists():
                print(f"{Fore.RED}{path} not found{Style.RESET_ALL}")
                continue

            if path.is_dir():
                iterator = sorted(path.rglob("*.py") if recursive else path.iterdir())
                for file_path in iterator:
                    self._append_python_path(file_path)
                continue

            self._append_python_path(path)

        if len(self.generator.py_files) < 1:
            print(f"{Fore.RED}no .py files found{Style.RESET_ALL}")
            return False

        return True


def build_parser() -> argparse.ArgumentParser:
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
        "--version",
        action="version",
        version="UMLement 0.2.0",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    init()

    try:
        script = UMLement()
        argvs_validated = script.validate_argvs_provided(args.paths, recursive=args.recursive)

        if not argvs_validated:
            raise ValueError("input validation failed")

        model_path = script.generate_class_inheritance_model()
        print(f"{Fore.CYAN}PlantUML model created: {model_path}{Style.RESET_ALL}")

        if args.model_only:
            print(f"{Fore.GREEN}model generation complete, diagram rendering skipped{Style.RESET_ALL}")
            return 0

        diagram_path = script.generate_class_inheritance_diagram(output_format=args.format)
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
