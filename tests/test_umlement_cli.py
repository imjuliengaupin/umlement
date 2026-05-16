import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from umlement import UMLement, build_parser, main


class TestValidateArgvsProvided:
    def test_accepts_python_file(self, tmp_path: Path) -> None:
        script_file = tmp_path / "demo.py"
        script_file.write_text("class Demo:\n    pass\n", encoding="utf-8")

        app = UMLement()

        assert app.validate_argvs_provided([str(script_file)]) is True
        assert app.generator.py_files == [str(script_file.resolve())]

    def test_rejects_missing_paths(self, tmp_path: Path) -> None:
        missing_file = tmp_path / "missing.py"

        app = UMLement()

        assert app.validate_argvs_provided([str(missing_file)]) is False
        assert app.generator.py_files == []

    def test_collects_only_python_files_from_folder(self, tmp_path: Path) -> None:
        python_file = tmp_path / "alpha.py"
        text_file = tmp_path / "notes.txt"
        nested_dir = tmp_path / "nested"
        python_file.write_text("class Alpha:\n    pass\n", encoding="utf-8")
        text_file.write_text("ignore me", encoding="utf-8")
        nested_dir.mkdir()

        app = UMLement()

        assert app.validate_argvs_provided([str(tmp_path)]) is True
        assert app.generator.py_files == [str(python_file.resolve())]

    def test_collects_python_files_recursively(self, tmp_path: Path) -> None:
        nested_dir = tmp_path / "nested"
        nested_dir.mkdir()
        nested_file = nested_dir / "beta.py"
        nested_file.write_text("class Beta:\n    pass\n", encoding="utf-8")

        app = UMLement()

        assert app.validate_argvs_provided([str(tmp_path)], recursive=True) is True
        assert app.generator.py_files == [str(nested_file.resolve())]

    def test_resets_previous_python_files_between_runs(self, tmp_path: Path) -> None:
        first_file = tmp_path / "first.py"
        second_file = tmp_path / "second.py"
        first_file.write_text("class First:\n    pass\n", encoding="utf-8")
        second_file.write_text("class Second:\n    pass\n", encoding="utf-8")

        app = UMLement()

        assert app.validate_argvs_provided([str(first_file)]) is True
        assert app.generator.py_files == [str(first_file.resolve())]

        assert app.validate_argvs_provided([str(second_file)]) is True
        assert app.generator.py_files == [str(second_file.resolve())]


class TestCliSurface:
    def test_build_parser_supports_model_only_flag(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["demo", "--model-only", "--progress", "--show-accessors"])

        assert args.model_only is True
        assert args.progress is True
        assert args.show_accessors is True
        assert args.format == "png"

    def test_main_returns_failure_for_missing_path(self) -> None:
        assert main(["definitely-missing.py"]) == 1
