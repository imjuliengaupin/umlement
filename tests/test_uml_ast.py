from pathlib import Path
import sys

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
    assert "Friend" in child.relationships
