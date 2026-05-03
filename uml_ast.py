from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class MethodInfo:
    name: str


@dataclass
class ClassInfo:
    name: str
    package: str
    bases: list[str] = field(default_factory=list)
    attributes: list[str] = field(default_factory=list)
    methods: list[MethodInfo] = field(default_factory=list)
    relationships: list[str] = field(default_factory=list)


class ClassVisitor(ast.NodeVisitor):
    def __init__(self, package: str) -> None:
        self.package = package
        self.classes: list[ClassInfo] = []
        self._current_class: ClassInfo | None = None

    def visit_ClassDef(self, node: ast.ClassDef) -> None:  # noqa: N802
        class_info = ClassInfo(
            name=node.name,
            package=self.package,
            bases=[self._render_name(base) for base in node.bases],
        )
        previous = self._current_class
        self._current_class = class_info
        for item in node.body:
            self.visit(item)
        self.classes.append(class_info)
        self._current_class = previous

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # noqa: N802
        if not self._current_class:
            return
        self._current_class.methods.append(MethodInfo(name=node.name))
        for child in ast.walk(node):
            if isinstance(child, ast.Assign):
                for target in child.targets:
                    self._capture_attribute_target(target)
            elif isinstance(child, ast.AnnAssign):
                self._capture_attribute_target(child.target)
            elif isinstance(child, ast.Call):
                relationship = self._render_name(child.func)
                if relationship and relationship not in self._current_class.relationships:
                    self._current_class.relationships.append(relationship)

    def _capture_attribute_target(self, target: ast.expr) -> None:
        if not self._current_class:
            return
        if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == "self":
            if target.attr not in self._current_class.attributes:
                self._current_class.attributes.append(target.attr)

    def _render_name(self, node: ast.AST) -> str:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            left = self._render_name(node.value)
            return f"{left}.{node.attr}" if left else node.attr
        if isinstance(node, ast.Subscript):
            return self._render_name(node.value)
        if isinstance(node, ast.Call):
            return self._render_name(node.func)
        return ""


def parse_python_file(path: str | Path) -> list[ClassInfo]:
    source_path = Path(path)
    module_name = source_path.stem
    tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
    visitor = ClassVisitor(package=module_name)
    visitor.visit(tree)
    return visitor.classes
