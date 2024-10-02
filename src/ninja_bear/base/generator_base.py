from __future__ import annotations
from abc import ABC, abstractmethod
import copy
from typing import Callable, List

from .info import VERSION
from .configuration_base import _DEFAULT_INDENT
from .generator_configuration import GeneratorConfiguration
from .generator_naming_conventions import GeneratorNamingConventions
from .name_converter import NamingConventionType, NameConverter
from .property import Property


class PropertyAlreadyExistsException(Exception):
    def __init__(self, property: str):
        super().__init__(f'Property {property} already exists')


class NoTypeNameProvidedException(Exception):
    def __init__(self):
        super().__init__('No type name has been provided')


class GeneratorBase(ABC):
    """
    Abstract class that acts as the base for all Generator implementations.
    """

    def __init__(
        self,
        config: GeneratorConfiguration,
        properties: List[Property] = [],
        additional_props = {}
    ):
        """
        Constructor

        :param config:           Generator configuration.
        :type config:            GeneratorConfiguration
        :param properties:       List of properties to generator by the GeneratorBase derivate, defaults to []
        :type properties:        List[Property], optional
        :param additional_props: All props that might need to be used by the derivating class, defaults to {}
        :type additional_props:  dict, optional
        """
        type_name = config.type_name
        indent = config.indent

        self.transform = config.transform
        self._properties: List[Property] = []
        self._naming_conventions = \
            config.naming_conventions if config.naming_conventions else GeneratorNamingConventions()
        self._additional_props = additional_props

        self._set_type_name(type_name)
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
        found_property = len([
            p for p in self._properties if p.name == property.name and p.namespace == property.namespace
        ]) > 0

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
        self._indent = indent if indent and indent >= 0 else _DEFAULT_INDENT
        return self

    def dump(self) -> str:
        """
        Generates a config file string.

        :return: Config file string.
        :rtype:  str
        """
        def add_newline(s):
            # Add trailing newline if required.
            if s[-1] != '\n':
                s += '\n'
            return s
        
        # Create copies of the properties to avoid messing around with the originals.
        properties_copy = [copy.deepcopy(property) for property in self._properties]

        # Transform properties if transform function was provided.
        self._apply_transformation(properties_copy)

        # Substitute property values.
        for property in properties_copy:
            Property.substitute(property, properties_copy)

        # Remove hidden properties.
        properties_copy = [property for property in properties_copy if not property.hidden]

        # Update property names according to naming convention.
        if self._naming_conventions.properties_naming_convention:
            for property in properties_copy:
                property.name = NameConverter.convert(
                    property.name, 
                    self._naming_conventions.properties_naming_convention
                )

        s = add_newline(self._dump(self._type_name, properties_copy))
        s += f'{self._line_comment(f"Generated with ninja-bear v{VERSION} (https://pypi.org/project/ninja-bear/).").strip()}'

        return add_newline(s)
    
    def get_type_name(self) -> str:
        """
        Returns the evaluated type name.

        :return: Evaluated type name.
        :rtype:  str
        """
        return self._type_name
    
    @abstractmethod
    def _default_type_naming_convention(self) -> NamingConventionType:
        """
        Abstract method which must be implemented by the deriving class to specify the default type naming convention.

        :return: Default naming convention.
        :rtype:  NamingConventionType
        """
        pass

    @abstractmethod
    def _line_comment(self, string: str) -> str:
        """
        Abstract method which must be implemented by the deriving class to turn a string into a line comment.

        :param string: String to turn into a line comment.
        :type string:  str

        :return: Commented string.
        :rtype:  str
        """
        pass

    @abstractmethod
    def _dump(self, type_name: str, properties: List[Property]) -> str:
        """
        Abstract method which must be implemented by the deriving class to create a type string.

        :param type_name:  Struct/class type-name.
        :type type_name:   str
        :param properties: Properties list.
        :type properties:  List[Property]

        :return: Dumped type string.
        :rtype:  str
        """
        pass

    def _set_type_name(self, name: str) -> GeneratorBase:
        """
        Sets the type name to the specified name. If no naming convention was set, the default
        naming convention, specified by the deriving class, will be used.

        :param name: Name of the generated type. HINT: This acts more like a template than the
                     real name as some conventions must be met and therefore the default convention
                     specified by the deriving class will be used if no naming convention for the
                     type name was provided (see _default_type_naming_convention).
        :type name:  str

        :raises NoTypeNameProvidedException: Raised if no name has been provided.

        :return: The current generator instance.
        :rtype:  Self
        """
        if not name:
            raise NoTypeNameProvidedException()
        naming_convention = self._naming_conventions.type_naming_convention

        self._type_name = NameConverter.convert(
            name,

            # Evaluate type naming convention. Use default if none was provided.
            naming_convention if naming_convention else self._default_type_naming_convention()
        )
        return self
    
    def _create_properties_string(self, callout: Callable[[Property], str], properties_copy: List[Property]) -> str:
        """
        Creates a string of all properties based on the provided callout.

        :param callout:         Callout to create a string based on the provided properties.
        :type callout:          Callable[[Property], str]
        :param properties_copy: Copy of all properties (to prevent modification of original).
        :type properties_copy:  List[Property]

        :return: Newline-separated properties string.
        :rtype:  str
        """
        return '\n'.join(
            # Loop in a loop. I know, it's a little bit confusing...
            property_string for property_string in [
                # This loop forms each property into a string.
                f'{callout(property)}' for property in properties_copy
            ] if property_string  # This clause makes sure that only property strings with a value are used.
        )
    
    def _apply_transformation(self, properties_copy: List[Property]) -> None:
        """
        Applies the user defined value transformation to each property value.

        :param properties_copy: Copy of all properties (to prevent modification of original).
        :type properties_copy:  List[Property]
        """
        if self.transform:
            NAME_KEY = 'name'
            VALUE_KEY = 'value'
            TYPE_KEY = 'type'
            PROPERTIES_KEY = 'properties'

            for i, property in enumerate(properties_copy):
                # Create dictionary for local variables. This dictionary will also be used
                # to get the modified value afterwards (https://stackoverflow.com/a/67824076).
                local_variables = {
                    NAME_KEY: property.name,
                    VALUE_KEY: property.value,
                    TYPE_KEY: property.type.value,
                    PROPERTIES_KEY: properties_copy,
                }

                # Execute user defined Python script.
                exec(self.transform, None, local_variables)
                
                # Create new property from modified value.
                properties_copy[i] = Property(
                    name=property.name,
                    value=local_variables[VALUE_KEY],
                    property_type=property.type,
                    hidden=property.hidden,
                    comment=property.comment,
                    namespace=property.namespace,
                )
