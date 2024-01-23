
import re as regex


class UMLRegex():

    def __init__(self) -> None:
        """initialize the regex patterns used for plantuml model generation"""
        self.is_newline_found: regex.Pattern = regex.compile(r"^\s*(:?$|#|raise|print)")
        self.is_base_class_found: regex.Pattern = regex.compile(r"^class\s+([\w\d]+)\(\)\s*:")
        self.is_child_class_found: regex.Pattern = regex.compile(r"^class\s+([\w\d]+)\(\s*([\w\d\._]+)\s*\):")
        self.is_class_attribute_found: regex.Pattern = regex.compile(r"^\s+self.([_\w]+)\s*=")
        self.is_private_class_attribute_found: regex.Pattern = regex.compile(r"^__[\w\d_]+")
        self.is_protected_class_attribute_found: regex.Pattern = regex.compile(r"^_[\w\d_]+")
        self.is_builtin_class_method_found: regex.Pattern = regex.compile(r"^__[\w_]+__")
        self.is_class_method_found: regex.Pattern = regex.compile(r"^\s+def (\w+)\(.*\):")
        self.is_private_class_method_found: regex.Pattern = regex.compile(r"^__[\w_]+")
        self.is_protected_class_method_found: regex.Pattern = regex.compile(r"^_[\w_]+")
        self.is_instantiated_class_found: regex.Pattern = regex.compile(r"((:?[A-Z]+[a-z0-9]+)+)\(.*\)")
