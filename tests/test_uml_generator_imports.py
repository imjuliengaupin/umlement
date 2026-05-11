import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from uml_generator import UMLGenerator


def test_generator_auto_includes_imported_sibling_modules(tmp_path: Path) -> None:
    helper = tmp_path / "helper.py"
    consumer = tmp_path / "consumer.py"
    helper.write_text("class Helper(object):\n    pass\n", encoding="utf-8")
    consumer.write_text(
        "from helper import Helper\n\n"
        "class Consumer(object):\n"
        "    def __init__(self):\n"
        "        self.helper = Helper()\n",
        encoding="utf-8",
    )

    generator = UMLGenerator()
    generator.py_files = [str(consumer)]

    model_path = generator.generate_class_inheritance_model()
    model_text = model_path.read_text(encoding="utf-8")

    assert "class Helper" in model_text
    assert "class Consumer" in model_text
    assert "Consumer *-- Helper : has-a (helper)" in model_text
