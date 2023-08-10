from enum import Enum


class PropertyType(Enum):
    """
    Enum of all supported property types.
    """
    BOOL = 0
    INT = 1
    FLOAT = 2
    DOUBLE = 3
    STRING = 4
    REGEX = 5
