from abc import ABC, abstractmethod
from typing import List

from .name_converter import NamingConventionType, NameConverter

from .property import Property


class PropertyAlreadyExistsException(Exception):
    def __init__(self, property: str):
        super().__init__(f'Property {property} already exists')


class NoClassNameProvidedException(Exception):
    def __init__(self):
        super().__init__('No class name has been provided')


class GeneratorBase(ABC):
    """
    Abstract class that acts as the base for all Generator implementations.
    """
    _DEFAULT_INDENT = 3

    def __init__(
        self,
        class_name: str,
        properties: List[Property] = [],
        indent: int = _DEFAULT_INDENT,
        additional_props = {}
    ):
        """
        Constructor

        :param class_name:       Name of the generated class. HINT: This acts more like a template than the real name
                                 as some conventions must be met and therefore the name might be changed in terms of
                                 casing (see also NameConverter).
        :type class_name:        str
        :param properties:       List of properties to generator by the GeneratorBase derivate, defaults to []
        :type properties:        List[Property], optional
        :param indent:           Whitespace indent before each property, defaults to _DEFAULT_INDENT
        :type indent:            int, optional
        :param additional_props: All props that might need to be used by the derivating class, defaults to {}
        :type additional_props:  dict, optional
        """
        self._properties: List[Property] = []
        self._additional_props = additional_props

        self._set_class_name(class_name)
        self.set_indent(indent)

        # Add properties one by one.
        [self.add_property(property) for property in properties]

    def add_property(self, property: Property):
        """
        Adds a property to the properties list. IMPORTANT: Property names must be unique.

        :param property: Property to add.
        :type property:  Property

        :raises PropertyAlreadyExistsException: Raised if the instance already contains a property with the same name.

        :return: The current generator instance.
        :rtype:  Self
        """
        found_property = len([p for p in self._properties if p.name == property.name]) > 0

        # Make sure that the name doesn't already exist.
        if found_property:
            raise PropertyAlreadyExistsException(property.name)

        self._properties.append(property)
        return self

    def set_indent(self, indent: int):
        """
        Sets the whitespace indent for the properties.

        :param indent: Indent value. If this value is less than 0, _DEFAULT_INDENT gets used.
        :type indent:  int

        :return: The current generator instance.
        :rtype:  Self
        """
        self._indent = indent if indent and indent >= 0 else self._DEFAULT_INDENT
        return self

    def dump(self) -> str:
        """
        Generates a config file string.

        :return: Config file string.
        :rtype:  str
        """
        s = self._before_class(**self._additional_props)
        s += f'{self._start_class()}\n'
        s += '\n'.join([f'{self._create_property_string(property)}' for property in self._properties])

        class_end = self._end_class()
        s += f'\n{class_end}'

        # Only append additional newline, if class_end is not empty
        if class_end:
            s += '\n'
        s += self._after_class(**self._additional_props)

        return s

    @abstractmethod
    def _create_property(self, property: Property) -> str:
        """
        Abstract method which must be implemented by the deriving class to generate a single property string.

        :param property: Property to generate a property string from.
        :type property:  Property

        :return: A language specific property string (e.g., "public static readonly myBoolean = true;").
        :rtype:  str
        """
        pass

    @abstractmethod
    def _create_comment(self, comment: str) -> str:
        """
        Abstract method which must be implemented by the deriving class to generate a comment string.

        :param comment: Comment value.
        :type comment:  str

        :return: A language specific comment string (e.g., /* This is a comment. */).
        :rtype:  str
        """
        pass

    @abstractmethod
    def _before_class(self, **props) -> str:
        """
        Abstract method which must be implemented by the deriving class to generate a possible string which will
        be added in front of the generated class/struct. If not required, this method shall return an empty string.

        :return: String to insert before the generated class/struct.
        :rtype:  str
        """
        pass

    @abstractmethod
    def _after_class(self, **props) -> str:
        """
        Abstract method which must be implemented by the deriving class to generate a possible string which will
        be added after the generated class/struct. If not required, this method shall return an empty string.

        :return: String to insert after the generated class/struct.
        :rtype:  str
        """
        pass

    @abstractmethod
    def _start_class(self) -> str:
        """
        Abstract method which must be implemented by the deriving class to generate the class'/struct's definition.

        :return: The generated class/struct definition (e.g., "export class TestConfig {").
        :rtype:  str
        """
        pass

    @abstractmethod
    def _end_class(self) -> str:
        """
        Abstract method which must be implemented by the deriving class to generate the class'/struct's body end.

        :return: The generated class'/struct's body end (e.g., "}").
        :rtype:  str
        """
        pass

    def _set_class_name(self, name: str):
        if not name:
            raise NoClassNameProvidedException()

        self._class_name = NameConverter.convert(name, NamingConventionType.PASCAL_CASE)
        return self

    def _create_property_string(self, property: Property) -> str:
        """
        Creates a property string from a property.

        :param property: Property to generate a property string from.
        :type property:  Property

        :return: A language specific property string including a possible comment (e.g.,
                 "public static readonly myBoolean = true;" /* This is a comment. */).
        :rtype:  str
        """
        s = ' ' * self._indent  # Indent space.
        s += self._create_property(property)

        if property.comment:
            s += self._create_comment(property.comment)
        return s
