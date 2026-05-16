"""In-memory UML model primitives used during PlantUML emission."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class UMLRelationship:
    """Directed relationship between two UML classes."""
    source: str
    target: str
    kind: str
    via: str | None = None


@dataclass
class UMLClass:
    """Renderable UML class definition with members and relationships."""
    name: str
    package: str
    bases: list[str] = field(default_factory=list)
    attributes: list[str] = field(default_factory=list)
    methods: list[str] = field(default_factory=list)
    relationships: list[UMLRelationship] = field(default_factory=list)


@dataclass
class UMLModel:
    """Aggregate container for the full UML model about to be rendered."""
    classes: list[UMLClass] = field(default_factory=list)

    def class_names(self) -> set[str]:
        """Return the set of class names present in the model for quick lookups."""
        return {uml_class.name for uml_class in self.classes}
