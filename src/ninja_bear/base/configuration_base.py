from dataclasses import dataclass
from typing import List


_DEFAULT_INDENT = 4


@dataclass(kw_only=True)  # https://medium.com/@aniscampos/python-dataclass-inheritance-finally-686eaf60fbb5
class ConfigurationBase:
    """
    Serves as the base for several configuration classes.
    """
    indent: int = _DEFAULT_INDENT
    """
    Whitespace indent before each property, defaults to _DEFAULT_INDENT
    """
    transformers: List[str] = None
    """
    Python scripts which can transform the provided value. The script has access to the following variables.
    - name: Property name.
    - value: Property value.
    - type: Property type value (see values PropertyType).
    - properties: List of all properties (must not be modified).

    To reflect changes to the outside of the script, the value variable must be modified.
    """
