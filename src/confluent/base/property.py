import re
from .property_type import PropertyType


class InvalidVariableNameException(Exception):
    def __init__(self, variable_name: str):
        super().__init__(f'{variable_name} is not a valid variable name')


class Property:
    """
    Holds all the required information to create a property string.

    :raises InvalidVariableNameException: Raised if an invalid variable name has been provided.
    """

    def __init__(
        self,
        name: str,
        value: str | bool | int | float,
        property_type: PropertyType,
        hidden: bool = False,
        comment: str = None
    ):
        """
        Constructor

        :param name:          Property name.
        :type name:           str
        :param value:         Property value.
        :type value:          str | bool | int | float
        :param property_type: Property type.
        :type property_type:  PropertyType
        :param hidden:        If True, the property will not be put out to the generated file, defaults to False
        :type hidden:         bool, optional
        :param comment:       Property description, defaults to None
        :type comment:        str, optional

        :raises InvalidVariableNameException: Raised if an invalid variable name has been provided.
        """
        # Check if the key is a valid variable name by Java standards.
        if not re.match(r'^(_|[a-zA-Z])\w*$', name):
            raise InvalidVariableNameException(name)
        
        # Make sure that the provided value is valid even if it's a string.
        if isinstance(value, str):
            match property_type:
                case PropertyType.BOOL:
                    # Correct boolean property value to 'true' or 'false'.
                    value = False if value.lower() in ['0', 'false', 'no', 'off'] else True
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
