"""Build PlantUML models and rendered diagrams from discovered Python source files."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from constants import OUTPUT_DIR, PLANTUML_HEADER_LINES, PLANTUML_MODEL_NAME, RESOURCES_DIR
from progress_types import ProgressSink
from uml_ast import parse_python_file
from uml_model import UMLClass, UMLModel, UMLRelationship
from umlement_progress import ProgressReporter


class UMLGenerator:
    """Translate parsed Python files into PlantUML model and diagram artifacts."""

    def __init__(
        self,
        progress: ProgressSink | None = None,
        show_accessors: bool = False,
    ) -> None:
        self.py_files: list[str] = []
        self.progress = progress or ProgressReporter(enabled=False)
        self.show_accessors = show_accessors

    def get_output_model_path(self) -> Path:
        """Return the canonical PlantUML model output path."""
        return Path(OUTPUT_DIR) / PLANTUML_MODEL_NAME

    def get_output_diagram_path(self, extension: str = ".png") -> Path:
        """Return the rendered diagram path for the requested file extension."""
        return self.get_output_model_path().with_suffix(extension)

    def _get_plantuml_jar_path(self) -> str:
        """Locate the single PlantUML jar bundled in the local resources directory."""
        jars = sorted(jar for jar in os.listdir(RESOURCES_DIR) if jar.endswith(".jar"))
        if len(jars) > 1:
            raise Exception(
                "multiple .jar files found in the resources directory, "
                "please remove all but one and try again"
            )
        if not jars:
            raise Exception(
                "no .jar file found in the resources directory, "
                "please add and try again"
            )
        return f"{RESOURCES_DIR}/{jars[0]}"

    def _expand_import_neighbor_files(self) -> None:
        """Auto-include sibling Python modules imported by already-queued source files."""
        discovered = set(self.py_files)
        # Neighbor auto-inclusion keeps small local projects readable in the UI
        # without requiring users to manually enumerate every imported sibling.
        added = True
        while added:
            added = False
            for py_file in list(discovered):
                file_path = Path(py_file)
                source = file_path.read_text(encoding="utf-8")
                for sibling in file_path.parent.glob("*.py"):
                    module_name = sibling.stem
                    if sibling == file_path:
                        continue
                    if f"from {module_name} import" in source or f"import {module_name}" in source:
                        resolved = str(sibling.resolve())
                        if resolved not in discovered:
                            discovered.add(resolved)
                            self.progress.info("Auto-included imported module", resolved)
                            added = True
        self.py_files = sorted(discovered)

    def build_model(self) -> UMLModel:
        """Parse queued Python files and assemble the in-memory UML model."""
        self._expand_import_neighbor_files()
        model = UMLModel()
        for py_file in self.py_files:
            self.progress.info("Scanning file", py_file)
            classes = parse_python_file(py_file)
            for item in classes:
                model.classes.append(
                    UMLClass(
                        name=item.name,
                        package=item.package,
                        bases=item.bases,
                        attributes=item.attributes,
                        methods=[method.name for method in item.methods],
                        relationships=[
                            UMLRelationship(
                                source=item.name,
                                target=relationship.target,
                                kind=relationship.kind,
                                via=relationship.via,
                            )
                            for relationship in item.relationships
                        ],
                    )
                )
        return model

    def generate_class_inheritance_model(self) -> Path:
        """Write a PlantUML model file for the currently queued Python sources."""
        self.progress.advance("Preparing model generation", f"{len(self.py_files)} Python file(s) queued")
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_model_path = self.get_output_model_path()
        model = self.build_model()
        known_classes = model.class_names()

        with open(output_model_path, "w", encoding="utf8") as plantuml_file:
            plantuml_file.write("@startuml\n")
            for line in PLANTUML_HEADER_LINES:
                plantuml_file.write(f"{line}\n")
            plantuml_file.write("skinparam classAttributeIconSize 0\n")
            plantuml_file.write("hide empty members\n")
            plantuml_file.write("\n")

            for uml_class in model.classes:
                stereotype = " <<entrypoint>>" if uml_class.name.lower().endswith(("app", "cli", "runner")) else ""
                plantuml_file.write(f"class {uml_class.name}{stereotype}\n")
                for attribute in uml_class.attributes:
                    plantuml_file.write(f"{uml_class.name} : +{attribute}\n")
                for method in uml_class.methods:
                    # Dunder methods add noise for this utility's intended
                    # reverse-engineering view, so they stay hidden.
                    if method.startswith("__") and method.endswith("__"):
                        continue
                    # Accessors are an explicit opt-in because the compact view is
                    # the default portfolio-friendly presentation.
                    if not self.show_accessors and method.startswith(("get_", "set_")):
                        continue
                    plantuml_file.write(f"{uml_class.name} : +{method}()\n")
                plantuml_file.write("\n")

            emitted_relationships: set[tuple[str, str, str, str | None]] = set()
            for uml_class in model.classes:
                for base in uml_class.bases:
                    base_name = base.split(".")[-1]
                    if base_name and base_name != "object":
                        plantuml_file.write(f"{base_name} <|-- {uml_class.name}\n")
                for relationship in uml_class.relationships:
                    # Only emit relationships that resolve to classes inside the
                    # current model, otherwise the diagram picks up noisy phantom edges.
                    if relationship.target not in known_classes or relationship.target == uml_class.name:
                        continue
                    key = (relationship.source, relationship.target, relationship.kind, relationship.via)
                    if key in emitted_relationships:
                        continue
                    emitted_relationships.add(key)
                    if relationship.kind == "has-a":
                        label = f" : has-a ({relationship.via})" if relationship.via else " : has-a"
                        plantuml_file.write(f"{relationship.source} *-- {relationship.target}{label}\n")
                    else:
                        plantuml_file.write(f"{relationship.source} ..> {relationship.target} : uses\n")

            plantuml_file.write("@enduml\n")

        self.progress.info("PlantUML model ready", str(output_model_path))
        return output_model_path

    def generate_class_inheritance_diagram(self, output_format: str = "png") -> Path:
        """Render the generated PlantUML model into the requested output image format."""
        self.progress.advance("Rendering diagram", f"output format: {output_format}")
        plantuml_jar = self._get_plantuml_jar_path()
        plantuml_model = str(self.get_output_model_path())
        plantuml_format = output_format.lower().lstrip(".")

        result = subprocess.run(
            ["java", "-jar", plantuml_jar, f"-t{plantuml_format}", plantuml_model],
            check=False,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise Exception(result.stderr.strip() or result.stdout.strip() or "PlantUML diagram generation failed")

        output_path = self.get_output_diagram_path(f".{plantuml_format}")
        self.progress.info("Diagram render complete", str(output_path))
        return output_path
