from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class MethodInfo:
    name: str


@dataclass
class RelationshipInfo:
    target: str
    kind: str
    via: str | None = None


@dataclass
class ClassInfo:
    name: str
    package: str
    bases: list[str] = field(default_factory=list)
    attributes: list[str] = field(default_factory=list)
    methods: list[MethodInfo] = field(default_factory=list)
    relationships: list[RelationshipInfo] = field(default_factory=list)
    imported_names: dict[str, str] = field(default_factory=dict)


class ClassVisitor(ast.NodeVisitor):
    def __init__(self, package: str, imported_names: dict[str, str]) -> None:
        self.package = package
        self.imported_names = imported_names
        self.classes: list[ClassInfo] = []
        self._current_class: ClassInfo | None = None

    def visit_ClassDef(self, node: ast.ClassDef) -> None:  # noqa: N802
        class_info = ClassInfo(
            name=node.name,
            package=self.package,
            bases=[self._render_name(base) for base in node.bases],
            imported_names=self.imported_names.copy(),
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
                    self._capture_relationship_from_assignment(target, child.value)
            elif isinstance(child, ast.AnnAssign):
                self._capture_attribute_target(child.target)
                if child.value is not None:
                    self._capture_relationship_from_assignment(child.target, child.value)
            elif isinstance(child, ast.Call):
                relationship = self._resolve_name(self._render_name(child.func))
                if relationship:
                    self._add_relationship(relationship, "uses")

    def _capture_attribute_target(self, target: ast.expr) -> None:
        if not self._current_class:
            return
        if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == "self":
            if target.attr not in self._current_class.attributes:
                self._current_class.attributes.append(target.attr)

    def _capture_relationship_from_assignment(self, target: ast.expr, value: ast.expr) -> None:
        if not self._current_class:
            return
        if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == "self":
            relationship = self._relationship_target_from_value(value)
            if relationship:
                self._add_relationship(relationship, "has-a", via=target.attr)

    def _relationship_target_from_value(self, value: ast.expr) -> str | None:
        if isinstance(value, ast.Call):
            return self._resolve_name(self._render_name(value.func))
        if isinstance(value, (ast.List, ast.Tuple, ast.Set)):
            for item in value.elts:
                if isinstance(item, ast.Call):
                    relationship = self._resolve_name(self._render_name(item.func))
                    if relationship:
                        return relationship
        return None

    def _add_relationship(self, target: str, kind: str, via: str | None = None) -> None:
        if not self._current_class or not target:
            return
        for relationship in self._current_class.relationships:
            if relationship.target == target and relationship.kind == kind and relationship.via == via:
                return
        self._current_class.relationships.append(RelationshipInfo(target=target, kind=kind, via=via))

    def _resolve_name(self, name: str) -> str:
        if not name:
            return ""
        if name in self.imported_names:
            return self.imported_names[name].split(".")[-1]
        return name.split(".")[-1]

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


def parse_imports(tree: ast.AST) -> dict[str, str]:
    imported_names: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                imported_names[alias.asname or alias.name] = f"{module}.{alias.name}" if module else alias.name
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imported_names[alias.asname or alias.name] = alias.name
    return imported_names


def parse_python_file(path: str | Path) -> list[ClassInfo]:
    source_path = Path(path)
    module_name = source_path.stem
    tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
    visitor = ClassVisitor(package=module_name, imported_names=parse_imports(tree))
    visitor.visit(tree)
    return visitor.classes
