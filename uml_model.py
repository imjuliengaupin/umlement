from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class UMLRelationship:
    source: str
    target: str
    kind: str
    via: str | None = None


@dataclass
class UMLClass:
    name: str
    package: str
    bases: list[str] = field(default_factory=list)
    attributes: list[str] = field(default_factory=list)
    methods: list[str] = field(default_factory=list)
    relationships: list[UMLRelationship] = field(default_factory=list)


@dataclass
class UMLModel:
    classes: list[UMLClass] = field(default_factory=list)

    def class_names(self) -> set[str]:
        return {uml_class.name for uml_class in self.classes}
