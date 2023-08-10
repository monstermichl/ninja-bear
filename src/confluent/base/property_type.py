from enum import IntEnum, auto


class PropertyType(IntEnum):
    """
    Enum of all supported property types.
    """
    BOOL = 1
    INT = auto()
    FLOAT = auto()
    DOUBLE = auto()
    STRING = auto()
    REGEX = auto()
