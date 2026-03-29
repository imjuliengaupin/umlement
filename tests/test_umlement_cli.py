from pathlib import Path

from umlement import UMLement


class TestValidateArgvsProvided:
    def test_accepts_python_file(self, tmp_path: Path) -> None:
        script_file = tmp_path / "demo.py"
        script_file.write_text("class Demo:\n    pass\n", encoding="utf-8")

        app = UMLement()

        assert app.validate_argvs_provided([str(script_file)]) is True
        assert app.generator.py_files == [str(script_file)]

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
        assert app.generator.py_files == [str(python_file)]

    def test_resets_previous_python_files_between_runs(self, tmp_path: Path) -> None:
        first_file = tmp_path / "first.py"
        second_file = tmp_path / "second.py"
        first_file.write_text("class First:\n    pass\n", encoding="utf-8")
        second_file.write_text("class Second:\n    pass\n", encoding="utf-8")

        app = UMLement()

        assert app.validate_argvs_provided([str(first_file)]) is True
        assert app.generator.py_files == [str(first_file)]

        assert app.validate_argvs_provided([str(second_file)]) is True
        assert app.generator.py_files == [str(second_file)]
