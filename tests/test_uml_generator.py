import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from uml_generator import UMLGenerator


def test_generate_class_inheritance_model_keeps_attributes_with_owning_class(tmp_path: Path) -> None:
    parent_file = tmp_path / "parent.py"
    child_file = tmp_path / "child.py"
    parent_file.write_text(
        "class Parent(object):\n"
        "    def __init__(self):\n"
        "        self.parent_value = 1\n",
        encoding="utf-8",
    )
    child_file.write_text(
        "from parent import Parent\n\n"
        "class Child(Parent):\n"
        "    def __init__(self):\n"
        "        self.child_value = 2\n",
        encoding="utf-8",
    )

    generator = UMLGenerator()
    generator.py_files = [str(parent_file), str(child_file)]

    model_path = generator.generate_class_inheritance_model()
    model_text = model_path.read_text(encoding="utf-8")

    assert "Parent : +parent_value" in model_text
    assert "Child : +child_value" in model_text
    assert "Parent : +child_value" not in model_text


def test_generate_class_inheritance_model_returns_model_path(tmp_path: Path) -> None:
    source_file = tmp_path / "tiny.py"
    source_file.write_text("class Demo(object):\n    pass\n", encoding="utf-8")

    generator = UMLGenerator()
    generator.py_files = [str(source_file)]

    model_path = generator.generate_class_inheritance_model()

    assert model_path.exists()
    assert model_path.suffix == ".puml"


def test_generate_class_inheritance_model_applies_custom_style_and_hides_dunder_methods(tmp_path: Path) -> None:
    source_file = tmp_path / "runner.py"
    source_file.write_text(
        "class DemoRunner(object):\n"
        "    def __init__(self):\n"
        "        self.path = 'x'\n"
        "    def execute(self):\n"
        "        return self.path\n",
        encoding="utf-8",
    )

    generator = UMLGenerator()
    generator.py_files = [str(source_file)]

    model_text = generator.generate_class_inheritance_model().read_text(encoding="utf-8")

    assert "HeaderBackgroundColor #E0E7FF" in model_text
    assert "class DemoRunner <<entrypoint>>" in model_text
    assert "DemoRunner : +execute()" in model_text
    assert "DemoRunner : +__init__()" not in model_text


def test_generate_class_inheritance_model_hides_accessors_by_default(tmp_path: Path) -> None:
    source_file = tmp_path / "coin.py"
    source_file.write_text(
        "class Coin(object):\n"
        "    def get_value(self):\n"
        "        return 1\n"
        "    def set_value(self, value):\n"
        "        self.value = value\n"
        "    def spend(self):\n"
        "        return True\n",
        encoding="utf-8",
    )

    generator = UMLGenerator()
    generator.py_files = [str(source_file)]

    model_text = generator.generate_class_inheritance_model().read_text(encoding="utf-8")

    assert "Coin : +get_value()" not in model_text
    assert "Coin : +set_value()" not in model_text
    assert "Coin : +spend()" in model_text


def test_generate_class_inheritance_model_can_show_accessors(tmp_path: Path) -> None:
    source_file = tmp_path / "coin.py"
    source_file.write_text(
        "class Coin(object):\n"
        "    def get_value(self):\n"
        "        return 1\n"
        "    def set_value(self, value):\n"
        "        self.value = value\n",
        encoding="utf-8",
    )

    generator = UMLGenerator(show_accessors=True)
    generator.py_files = [str(source_file)]

    model_text = generator.generate_class_inheritance_model().read_text(encoding="utf-8")

    assert "Coin : +get_value()" in model_text
    assert "Coin : +set_value()" in model_text
