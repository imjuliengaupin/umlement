
import io
import os
import subprocess
from constants import PLANTUML_MODEL_DIR, PLANTUML_MODEL_NAME, RESOURCES_DIR
from uml_regex import UMLRegex


class UMLGenerator():

    def __init__(self) -> None:
        self.py_files: list = []
        self.py_scanner: UMLRegex = UMLRegex()
        self.class_name: str = str()
        self.classes: list = []
        self.class_attributes: dict = {}
        self.class_relationships: dict = {}
        self.parents: dict = {}

    def generate_class_inheritance_diagram(self) -> None:
        """a method to execute a java subprocess which generates a plantuml class inheritance diagram `.png` in the local project directory"""
        jars: list[str] = [jar for jar in os.listdir(RESOURCES_DIR) if jar.endswith(".jar")]

        if len(jars) > 1:
            raise Exception("multiple .jar files found in the resources directory, please remove all but one and try again")
        elif not jars:
            raise Exception("no .jar file found in the resources directory, please add and try again")
        else:
            plantuml_jar_name: str = jars[0]

        PLANTUML_JAR: str = f"{RESOURCES_DIR}/{plantuml_jar_name}"
        PLANTUML_MODEL: str = f"{PLANTUML_MODEL_DIR}/{PLANTUML_MODEL_NAME}"

        subprocess.call(["java", "-jar", PLANTUML_JAR, PLANTUML_MODEL])

    def generate_class_inheritance_model(self) -> None:
        """a method to scan each `.py` file in the argvs list and write programatically generated UML to a `.puml` file in the local project directory"""

        # create a new folder in the local project directory to store the `.puml` file and class inheritance diagram `.png`
        if not os.path.exists(PLANTUML_MODEL_DIR):
            os.makedirs(PLANTUML_MODEL_DIR)

        # create a new `.puml` file in the local project directory
        with open(f"{PLANTUML_MODEL_DIR}/{PLANTUML_MODEL_NAME}", 'w', encoding="utf8") as plantuml_file:

            # write a conventional UML header to the `.puml` file
            plantuml_file.write("@startuml\n")

            # for each `.py` file passed to the script argvs list
            for py_file in self.py_files:

                # capture the index position of each `.py` file in the argvs list
                i: int = self.py_files.index(py_file)

                # write the `.py` package name in UML notation to the `.puml` file
                self.write_class_packages_uml_notation(plantuml_file, i)

                # scan each `.py` code file and write the `.py` class methods in UML notation to the `.puml` file
                self.python_code_scan(plantuml_file, py_file)

                # write the `.py` class attributes in UML notation to the `.puml` file
                self.write_class_attributes_uml_notation(plantuml_file)

            # write the `.py` class relationships in UML notation to the `.puml` file
            self.write_class_relationships_uml_notation(plantuml_file)

            # write a conventional UML footer to the `.puml` file
            plantuml_file.write("@enduml\n")

    def python_code_scan(self, plantuml_file: io.TextIOWrapper, py_file: str) -> None:
        """a method to scan `.py` file source code to extract class figure details"""

        # for each line of code in the `.py` file being read
        for line_of_code in open(py_file, 'r', encoding="utf8"):

            # if a newline `\n` is scanned in the `.py` code file being read, ignore it and continue to scan the next line of code
            if self.py_scanner.is_newline_found.match(line_of_code):
                continue

            # #######################################################################
            # if any code for a class that does not have a parent is scanned

            # read the regex string result and compare it against the syntax pattern of a defined `.py` base class, e.g. `class Parent():`
            base_class_found = self.py_scanner.is_base_class_found.match(line_of_code)

            # if a pattern is found that matches the syntax of a defined `.py` base class
            if base_class_found:

                # save the base class name
                base_class_name: str = base_class_found.group(1)

                # write the base (parent) or child class name to the `.puml` file
                self.write_class_names_uml_notation(plantuml_file, base_class_name, "")

                continue

            # #######################################################################
            # if any code for a class that has a parent is found

            # read the regex string result and compare it against the syntax pattern of a defined `.py` parent-child class relationship, e.g. `class Parent(Child):`
            child_class_found = self.py_scanner.is_child_class_found.match(line_of_code)

            # if a pattern is found that matches the syntax of a defined `.py` parent-child class relationship
            if child_class_found:

                # save the parent and child class names
                # reference https://docs.python.org/3/library/re.html#re.Match.group
                child_class_name: str = child_class_found.group(1)
                parent_class_name: str = child_class_found.group(2)

                # write the base (parent) or child class name to the `.puml` file
                self.write_class_names_uml_notation(plantuml_file, child_class_name, parent_class_name)

                continue

            # #######################################################################
            # if any class variable definition or initialization code is found

            # read the regex string result and compare it against the syntax pattern of the definition or initialization of a `.py` class variable
            class_variable_found = self.py_scanner.is_class_attribute_found.match(line_of_code)

            # if a pattern is found that matches the syntax of the definition or initialization of a `.py` class variable
            if class_variable_found and self.class_name:

                # save the class variable name
                class_variable_name: str = class_variable_found.group(1)

                # append the class variable name and access modifier (if set) to the list of class variables
                self.set_class_attributes(class_variable_name)

                continue

            # #######################################################################
            # if any class method definition or instantiation code is found

            # read the regex string result and compare it against the syntax pattern of the definition or instantiation of a `.py` class method
            class_method_found = self.py_scanner.is_class_method_found.match(line_of_code)

            # if a pattern is found that matches the syntax of the definition or instantiation of a `.py` class method
            if class_method_found and self.class_name:

                # save the class method name
                class_method_name: str = class_method_found.group(1)

                # write the class method name and access modifier (if set) to the `.puml` file
                self.write_class_methods_uml_notation(plantuml_file, class_method_name)

                continue

            # #######################################################################
            # if any class object instantiation code is found

            # search the regex string result and compare it against the syntax pattern of `.py` class object instantiation
            # reference https://docs.python.org/3/library/re.html#search-vs-match
            # reference https://docs.python.org/3/library/re.html#re.search
            class_instantiation_found = self.py_scanner.is_instantiated_class_found.search(line_of_code)

            # if a pattern is found that matches the syntax of `.py` class object instantiation
            if class_instantiation_found and self.class_name:

                # save the instantiated class name
                instantiated_class_name: str = class_instantiation_found.group(1)

                # append the instantiated class name to the list of class relationships
                self.set_class_instantiation_relationships(instantiated_class_name)

                continue

    def write_class_packages_uml_notation(self, plantuml_file: io.TextIOWrapper, i: int) -> None:
        """a method to write `.py` class package names in UML notation to a `.puml` file"""

        # extract the class package name from each `.py` file contained in the argvs list
        class_package_name: str = self.set_class_package_uml_representation(i)

        # write the `.py` class package name in UML notation to the `.puml` file
        plantuml_file.write(f"package {class_package_name} {{\n")

    def write_class_names_uml_notation(self, plantuml_file: io.TextIOWrapper, base_or_child_class_name: str, parent_class_name: str) -> None:
        """a method to write `.py` class names in UML notation to a `.puml` file"""

        # if a base (or child) class name scanned is already in the classes list, ignore it and return to scanning the `.py` code until a class name is found that is not yet in the list
        if base_or_child_class_name in self.classes:
            return

        # when a new base (or child) class name is scanned, append it to the classes list
        self.classes.append(base_or_child_class_name)

        # set the base (or child) class name to the UMLGenerator class name attribute
        self.class_name = base_or_child_class_name

        # initialize the class attributes dictionary for the base (or child) class, e.g. `{ class : [attribute, attribute, ...] }`
        self.class_attributes[base_or_child_class_name] = []

        # initialize the parent-child class associations dictionary for the base (or child) class, e.g. `{ parent : child }`
        self.parents[base_or_child_class_name] = parent_class_name

        # initialize the class relationship dictionary for the base (or child) class, e.g. `{ class : [relationship, relationship, ...] }`
        self.class_relationships[base_or_child_class_name] = []

        # write the `.py` class name in UML notation to the `.puml` file
        plantuml_file.write(f"class {base_or_child_class_name}\n")

    def write_class_attributes_uml_notation(self, plantuml_file: io.TextIOWrapper) -> None:
        """a method to write `.py` class attributes w/ access modifier details (if set) in UML notation to a `.puml` file"""

        # write the `.py` class attribute w/ access modifier details (if set) and any associations it has to other `.py` classes in UML notation to the `.puml` file
        for class_name, class_attributes in self.class_attributes.items():
            for class_attribute in class_attributes:
                plantuml_file.write(f"{class_name} : {class_attribute}\n")

        # write additional UML formatting to the `.puml` file
        plantuml_file.write("}\n\n")

    def write_class_methods_uml_notation(self, plantuml_file: io.TextIOWrapper, class_method_name: str) -> None:
        """a method to write `.py` class methods (including built-in methods) w/ access modifier details (if set) in UML notation to a `.puml` file"""

        # extract the class method w/ access modifier details (if set)
        class_method: str = self.set_class_method_uml_representation(class_method_name)

        # write the `.py` class method and any associations it has to other `.py` classes in UML notation to the `.puml` file
        plantuml_file.write(f"{self.class_name} : {class_method}()\n")

    def write_class_relationships_uml_notation(self, plantuml_file: io.TextIOWrapper) -> None:
        """a method to write `.py` class relationships in UML notation to a `.puml` file"""

        for child_class, parent_class in self.parents.items():
            # if a child class does not have a defined parent class, or if a parent class inherits from `object`, ignore it and continue to check the next class in the parents dictionary
            if not parent_class or parent_class == "object":
                continue

            # write the `.py` parent-child class relationship in UML notation to the `.puml` file
            plantuml_file.write(f"{parent_class} <|-- {child_class}\n")

        # write the `.py` instantiated class relationship in UML notation to the `.puml` file
        for class_name, classes in self.class_relationships.items():
            for instantiated_class in classes:
                if instantiated_class in self.classes and class_name != instantiated_class:
                    plantuml_file.write(f"{class_name} -- {instantiated_class}\n")

    def set_class_package_uml_representation(self, i: int) -> str:
        """a method to capture each `.py` class package name"""
        return os.path.basename(self.py_files[i].split('.')[0])

    def set_class_attribute_uml_representation(self, class_attribute_name: str) -> str:
        """a method to define the UML representation of `.py` class attributes w/ access modifier details (if set)"""

        # for private class attributes, e.g. `self.__var`
        if self.py_scanner.is_private_class_attribute_found.match(class_attribute_name):
            return f"-{class_attribute_name}"

        # for protected class attributes, e.g. `self._var`
        if self.py_scanner.is_protected_class_attribute_found.match(class_attribute_name):
            return f"#{class_attribute_name}"

        # for public class attributes, e.g. `self.var`
        return f"+{class_attribute_name}"

    def set_class_method_uml_representation(self, class_method_name: str) -> str:
        """a method to define the UML representation of `.py` class methods (including built-in methods) w/ access modifier details (if set)"""

        # for built-in class methods, e.g. `__init__()`, `__str__()`, etc.
        if self.py_scanner.is_builtin_class_method_found.match(class_method_name):
            return f"+{class_method_name}"

        # for private class methods, e.g. `__method()`
        if self.py_scanner.is_private_class_method_found.match(class_method_name):
            return f"-{class_method_name}"

        # for protected class methods, e.g. `_method()`
        if self.py_scanner.is_protected_class_method_found.match(class_method_name):
            return f"#{class_method_name}"

        # for public class methods, e.g. `method()`
        return f"+{class_method_name}"

    def set_class_attributes(self, class_attribute_name: str) -> None:
        """a method to append all instances of a `.py` class attribute w/ access modifier details to a dictionary"""

        # extract the class attribute w/ access modifier details (if set)
        class_attribute: str = self.set_class_attribute_uml_representation(class_attribute_name)

        # if the class attribute w/ access modifier details identified is not already in the class attributes dictionary, append it
        if class_attribute not in self.class_attributes[self.class_name]:
            self.class_attributes[self.class_name].append(class_attribute)

    def set_class_instantiation_relationships(self, instantiated_class_name: str) -> None:
        """a method to append all instances of a `.py` class being instantiated to a dictionary"""

        # if the instantiated class name identified is not already in the class relationships dictionary, append it
        if instantiated_class_name not in self.class_relationships[self.class_name]:
            self.class_relationships[self.class_name].append(instantiated_class_name)
