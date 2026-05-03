from __future__ import annotations

import os
import subprocess
from pathlib import Path

from constants import OUTPUT_DIR, PLANTUML_MODEL_NAME, RESOURCES_DIR
from uml_ast import parse_python_file
from uml_model import UMLClass, UMLModel
from umlement_progress import ProgressReporter


class UMLGenerator:
    def __init__(self, progress: ProgressReporter | None = None) -> None:
        self.py_files: list[str] = []
        self.progress = progress or ProgressReporter(enabled=False)

    def get_output_model_path(self) -> Path:
        return Path(OUTPUT_DIR) / PLANTUML_MODEL_NAME

    def get_output_diagram_path(self, extension: str = ".png") -> Path:
        return self.get_output_model_path().with_suffix(extension)

    def _get_plantuml_jar_path(self) -> str:
        jars = sorted(jar for jar in os.listdir(RESOURCES_DIR) if jar.endswith(".jar"))
        if len(jars) > 1:
            raise Exception("multiple .jar files found in the resources directory, please remove all but one and try again")
        if not jars:
            raise Exception("no .jar file found in the resources directory, please add and try again")
        return f"{RESOURCES_DIR}/{jars[0]}"

    def build_model(self) -> UMLModel:
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
                        relationships=item.relationships,
                    )
                )
        return model

    def generate_class_inheritance_model(self) -> Path:
        self.progress.advance("Preparing model generation", f"{len(self.py_files)} Python file(s) queued")
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_model_path = self.get_output_model_path()
        model = self.build_model()
        known_classes = model.class_names()

        package_map: dict[str, list[UMLClass]] = {}
        for uml_class in model.classes:
            package_map.setdefault(uml_class.package, []).append(uml_class)

        with open(output_model_path, "w", encoding="utf8") as plantuml_file:
            plantuml_file.write("@startuml\n")
            plantuml_file.write("skinparam classAttributeIconSize 0\n")
            plantuml_file.write("hide empty members\n")
            plantuml_file.write("left to right direction\n\n")

            for package_name, classes in sorted(package_map.items()):
                plantuml_file.write(f"package {package_name} {{\n")
                for uml_class in classes:
                    plantuml_file.write(f"class {uml_class.name}\n")
                    for attribute in uml_class.attributes:
                        plantuml_file.write(f"{uml_class.name} : +{attribute}\n")
                    for method in uml_class.methods:
                        plantuml_file.write(f"{uml_class.name} : +{method}()\n")
                plantuml_file.write("}\n\n")

            for uml_class in model.classes:
                for base in uml_class.bases:
                    base_name = base.split(".")[-1]
                    if base_name and base_name != "object":
                        plantuml_file.write(f"{base_name} <|-- {uml_class.name}\n")
                for relationship in uml_class.relationships:
                    relationship_name = relationship.split(".")[-1]
                    if relationship_name in known_classes and relationship_name != uml_class.name:
                        plantuml_file.write(f"{uml_class.name} -- {relationship_name}\n")

            plantuml_file.write("@enduml\n")

        self.progress.info("PlantUML model ready", str(output_model_path))
        return output_model_path

    def generate_class_inheritance_diagram(self, output_format: str = "png") -> Path:
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
