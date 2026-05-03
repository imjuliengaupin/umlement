from pathlib import Path
import sys

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
