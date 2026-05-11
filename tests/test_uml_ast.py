import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from uml_ast import parse_python_file


def test_parse_python_file_extracts_classes_and_relationships(tmp_path: Path) -> None:
    source = tmp_path / "sample.py"
    source.write_text(
        "class Base(object):\n"
        "    def __init__(self):\n"
        "        self.energy = 1\n"
        "\n"
        "class Friend(object):\n"
        "    pass\n"
        "\n"
        "class Child(Base):\n"
        "    def __init__(self):\n"
        "        self.friend = Friend()\n"
        "        self.mode = 'active'\n",
        encoding="utf-8",
    )

    classes = parse_python_file(source)
    names = {item.name for item in classes}
    child = next(item for item in classes if item.name == "Child")

    assert names == {"Base", "Friend", "Child"}
    assert child.bases == ["Base"]
    assert "friend" in child.attributes
    assert any(rel.target == "Friend" and rel.kind == "has-a" and rel.via == "friend" for rel in child.relationships)


def test_parse_python_file_resolves_imported_class_names(tmp_path: Path) -> None:
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

    classes = parse_python_file(consumer)
    consumer_class = next(item for item in classes if item.name == "Consumer")

    assert any(rel.target == "Helper" for rel in consumer_class.relationships)
