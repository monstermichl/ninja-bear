import re
from .property_type import PropertyType


class Property:
    def __init__(self, name: str, value: str | bool | int | float, property_type: PropertyType, hidden = False, comment = None):
        # Check if the key is a valid variable name by Java standards.
        if not re.match(r'^(_|[a-zA-Z])\w*$', name):
            raise Exception(f'Key {name} is not a valid variable name')
        
        # Make sure that the provided value is valid even if it's a string.
        if type(value) is str:
            match property_type:
                case PropertyType.BOOL:
                    value = True if value.lower() in ['1', 'true', 'yes', 'on'] else False  # Correct boolean property value to 'true' or 'false'.
                case PropertyType.INT:
                    match = re.match(r'\d+', value)
                    value = int(match.group(0)) if match else 0  # Remove everything that comes after the integer.
                case PropertyType.FLOAT | PropertyType.DOUBLE:
                    match = re.match(r'\d+(\.\d+)?', value)
                    value = float(match.group(0)) if match else 0  # Remove everything that comes after the float.

        self.name = name
        self.value = value
        self.type = property_type
        self.hidden = hidden
        self.comment = comment
