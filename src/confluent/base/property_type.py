from enum import IntEnum, auto


class PropertyType(IntEnum):
    """
    Enum of all supported property types.
    """
    BOOL = auto()
    INT = auto()
    FLOAT = auto()
    DOUBLE = auto()
    STRING = auto()
    REGEX = auto()
