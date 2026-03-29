#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import shutil
import sys
from colorama import (init, deinit, Fore, Style)
from constants import PLANTUML_MODEL_DIR
from uml_generator import UMLGenerator


class UMLement():

    def __init__(self) -> None:
        self.generator: UMLGenerator = UMLGenerator()

    def generate_class_inheritance_model(self):
        self.generator.generate_class_inheritance_model()

    def generate_class_inheritance_diagram(self):
        self.generator.generate_class_inheritance_diagram()

    def _append_python_path(self, path: Path) -> None:
        if path.is_file() and path.suffix.lower() == ".py":
            self.generator.py_files.append(str(path))
            return

        print(rf"{Fore.LIGHTBLACK_EX}{path} ignored, non-python files are unsupported{Style.RESET_ALL}")

    def validate_argvs_provided(self, argvs_provided: list[str]) -> bool:
        min_argvs_required: int = 1

        # check if any script argvs have been provided
        if len(argvs_provided) < min_argvs_required:
            print(f"{Fore.RED}an insufficient # of script arguments were provided (provided: {len(argvs_provided)}, expected: {min_argvs_required}){Style.RESET_ALL}")
            return False

        self.generator.py_files = []

        for argv in argvs_provided:
            path = Path(argv)

            if not path.exists():
                print(f"{Fore.RED}{path} not found{Style.RESET_ALL}")
                continue

            if path.is_dir():
                for file_path in sorted(path.iterdir()):
                    self._append_python_path(file_path)
                continue

            self._append_python_path(path)

        # check if atleast 1 index in the self.generator.py_files list contains a `.py` file
        if len(self.generator.py_files) < 1:
            print(f"{Fore.RED}no .py files found{Style.RESET_ALL}")
            return False

        return True


if __name__ == "__main__":
    try:
        init()

        # splice out the script name from the `sys.argv` list
        argvs: list[str] = sys.argv[1:]

        script: UMLement = UMLement()

        # validate each script argv provided
        argvs_validated: bool = script.validate_argvs_provided(argvs)

        if argvs_validated:
            # generate a plantuml class inheritance model built from the `.py` files passed as script argvs
            script.generate_class_inheritance_model()

            # generate a class inheritance diagram built from the plantuml model generated
            script.generate_class_inheritance_diagram()

            print(f"{Fore.GREEN}class inheritance model & diagram created successfully{Style.RESET_ALL}")

        else:
            raise Exception()

        deinit()

    except Exception as e:
        print(f"{Fore.RED}class inheritance model & diagram creation failed: {e}{Style.RESET_ALL}")

        # remove the directory containing any partically created `.puml` model and/or `.png` diagram files
        if Path(PLANTUML_MODEL_DIR).exists():
            shutil.rmtree(f"{PLANTUML_MODEL_DIR}")
