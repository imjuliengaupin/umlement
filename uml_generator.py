import io
import os
import subprocess
from pathlib import Path
from constants import OUTPUT_DIR, PLANTUML_MODEL_NAME, RESOURCES_DIR
from uml_regex import UMLRegex
from umlement_progress import ProgressReporter


class UMLGenerator():

    def __init__(self, progress: ProgressReporter | None = None) -> None:
        self.py_files: list[str] = []
        self.py_scanner: UMLRegex = UMLRegex()
        self.progress = progress or ProgressReporter(enabled=False)
        self.class_name: str = ""
        self.classes: list[str] = []
        self.class_attributes: dict[str, list[str]] = {}
        self.class_relationships: dict[str, list[str]] = {}
        self.parents: dict[str, str] = {}

    def reset_state(self) -> None:
        self.class_name = ""
        self.classes = []
        self.class_attributes = {}
        self.class_relationships = {}
        self.parents = {}

    def get_output_model_path(self) -> Path:
        return Path(OUTPUT_DIR) / PLANTUML_MODEL_NAME

    def get_output_diagram_path(self, extension: str = ".png") -> Path:
        return self.get_output_model_path().with_suffix(extension)

    def _get_plantuml_jar_path(self) -> str:
        jars: list[str] = sorted(jar for jar in os.listdir(RESOURCES_DIR) if jar.endswith(".jar"))

        if len(jars) > 1:
            raise Exception("multiple .jar files found in the resources directory, please remove all but one and try again")
        if not jars:
            raise Exception("no .jar file found in the resources directory, please add and try again")

        return f"{RESOURCES_DIR}/{jars[0]}"

    def generate_class_inheritance_diagram(self, output_format: str = "png") -> Path:
        """execute PlantUML to generate a diagram from the generated model"""
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

    def generate_class_inheritance_model(self) -> Path:
        """scan the collected Python files and generate a PlantUML model"""

        self.progress.advance("Preparing model generation", f"{len(self.py_files)} Python file(s) queued")
        self.reset_state()
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_model_path = self.get_output_model_path()

        with open(output_model_path, 'w', encoding="utf8") as plantuml_file:
            plantuml_file.write("@startuml\n")
            plantuml_file.write("skinparam classAttributeIconSize 0\n")
            plantuml_file.write("hide empty members\n\n")

            for i, py_file in enumerate(self.py_files):
                self.progress.info("Scanning file", py_file)
                self.write_class_packages_uml_notation(plantuml_file, i)
                self.python_code_scan(plantuml_file, py_file)
                self.write_class_attributes_uml_notation(plantuml_file)

            self.write_class_relationships_uml_notation(plantuml_file)
            plantuml_file.write("@enduml\n")

        self.progress.info("PlantUML model ready", str(output_model_path))
        return output_model_path

    def python_code_scan(self, plantuml_file: io.TextIOWrapper, py_file: str) -> None:
        """scan a Python file source code to extract class figure details"""

        active_class_name = ""

        with open(py_file, 'r', encoding="utf8") as source_file:
            for line_of_code in source_file:
                if self.py_scanner.is_newline_found.match(line_of_code):
                    continue

                base_class_found = self.py_scanner.is_base_class_found.match(line_of_code)
                if base_class_found:
                    active_class_name = base_class_found.group(1)
                    self.write_class_names_uml_notation(plantuml_file, active_class_name, "")
                    continue

                child_class_found = self.py_scanner.is_child_class_found.match(line_of_code)
                if child_class_found:
                    active_class_name = child_class_found.group(1)
                    parent_class_name: str = child_class_found.group(2)
                    self.write_class_names_uml_notation(plantuml_file, active_class_name, parent_class_name)
                    continue

                if not active_class_name:
                    continue

                self.class_name = active_class_name

                if line_of_code.startswith(("class ", "def ")):
                    continue

                class_variable_found = self.py_scanner.is_class_attribute_found.match(line_of_code)
                if class_variable_found:
                    self.set_class_attributes(class_variable_found.group(1))
                    continue

                class_method_found = self.py_scanner.is_class_method_found.match(line_of_code)
                if class_method_found:
                    self.write_class_methods_uml_notation(plantuml_file, class_method_found.group(1))
                    continue

                class_instantiation_found = self.py_scanner.is_instantiated_class_found.search(line_of_code)
                if class_instantiation_found:
                    self.set_class_instantiation_relationships(class_instantiation_found.group(1))
                    continue

    def write_class_packages_uml_notation(self, plantuml_file: io.TextIOWrapper, i: int) -> None:
        class_package_name: str = self.set_class_package_uml_representation(i)
        plantuml_file.write(f"package {class_package_name} {{\n")

    def write_class_names_uml_notation(self, plantuml_file: io.TextIOWrapper, base_or_child_class_name: str, parent_class_name: str) -> None:
        if base_or_child_class_name in self.classes:
            return

        self.classes.append(base_or_child_class_name)
        self.class_name = base_or_child_class_name
        self.class_attributes[base_or_child_class_name] = []
        self.parents[base_or_child_class_name] = parent_class_name
        self.class_relationships[base_or_child_class_name] = []
        plantuml_file.write(f"class {base_or_child_class_name}\n")

    def write_class_attributes_uml_notation(self, plantuml_file: io.TextIOWrapper) -> None:
        current_class_name = self.class_name
        if current_class_name:
            for class_attribute in self.class_attributes.get(current_class_name, []):
                plantuml_file.write(f"{current_class_name} : {class_attribute}\n")

        plantuml_file.write("}\n\n")

    def write_class_methods_uml_notation(self, plantuml_file: io.TextIOWrapper, class_method_name: str) -> None:
        class_method: str = self.set_class_method_uml_representation(class_method_name)
        plantuml_file.write(f"{self.class_name} : {class_method}()\n")

    def write_class_relationships_uml_notation(self, plantuml_file: io.TextIOWrapper) -> None:
        for child_class, parent_class in self.parents.items():
            if not parent_class or parent_class == "object":
                continue
            plantuml_file.write(f"{parent_class} <|-- {child_class}\n")

        for class_name, classes in self.class_relationships.items():
            for instantiated_class in classes:
                if instantiated_class in self.classes and class_name != instantiated_class:
                    plantuml_file.write(f"{class_name} -- {instantiated_class}\n")

    def set_class_package_uml_representation(self, i: int) -> str:
        return os.path.basename(self.py_files[i].split('.')[0])

    def set_class_attribute_uml_representation(self, class_attribute_name: str) -> str:
        if self.py_scanner.is_private_class_attribute_found.match(class_attribute_name):
            return f"-{class_attribute_name}"
        if self.py_scanner.is_protected_class_attribute_found.match(class_attribute_name):
            return f"#{class_attribute_name}"
        return f"+{class_attribute_name}"

    def set_class_method_uml_representation(self, class_method_name: str) -> str:
        if self.py_scanner.is_builtin_class_method_found.match(class_method_name):
            return f"+{class_method_name}"
        if self.py_scanner.is_private_class_method_found.match(class_method_name):
            return f"-{class_method_name}"
        if self.py_scanner.is_protected_class_method_found.match(class_method_name):
            return f"#{class_method_name}"
        return f"+{class_method_name}"

    def set_class_attributes(self, class_attribute_name: str) -> None:
        class_attribute: str = self.set_class_attribute_uml_representation(class_attribute_name)
        if class_attribute not in self.class_attributes[self.class_name]:
            self.class_attributes[self.class_name].append(class_attribute)

    def set_class_instantiation_relationships(self, instantiated_class_name: str) -> None:
        if instantiated_class_name not in self.class_relationships[self.class_name]:
            self.class_relationships[self.class_name].append(instantiated_class_name)
