from __future__ import annotations
from abc import ABC, abstractmethod
import copy
import datetime
import os
from typing import Dict, List

from .info import VERSION
from .configuration_base import _DEFAULT_INDENT
from .generator_configuration import GeneratorConfiguration
from .generator_naming_conventions import GeneratorNamingConventions
from .name_converter import NamingConventionType, NameConverter
from .property import Property
from .dump_info import DumpInfo


class PropertyAlreadyExistsException(Exception):
    def __init__(self, property: str):
        super().__init__(f'Property {property} already exists')


class NoTypeNameProvidedException(Exception):
    def __init__(self):
        super().__init__('No type name has been provided')


class InvalidDumpTypeException(Exception):
    def __init__(self):
        super().__init__('The returned dump value is not a string')


class GeneratorBase(ABC):
    """
    Abstract class that acts as the base for all Generator implementations.
    """

    def __init__(
        self,
        config: GeneratorConfiguration,
        properties: List[Property]=None,
        additional_props: Dict[str, any]=None
    ):
        """
        Constructor

        :param config:           Generator configuration.
        :type config:            GeneratorConfiguration
        :param properties:       List of properties to generator by the GeneratorBase derivate, defaults to None
        :type properties:        List[Property], optional
        :param additional_props: All props that might need to be used by the derivating class, defaults to None
        :type additional_props:  Dict[str, any], optional
        """
        type_name = config.type_name
        indent = config.indent

        # Since a default list cannot be assigned to parameters in the method header, because it only gets initialized
        # once and then the list gets re-used (see https://stackoverflow.com/a/1145781), make sure to set undefined
        # variables to list (see also https://docs.python.org/3/reference/compound_stmts.html#function-definitions).
        if not properties:
            properties = []
        if not additional_props:
            additional_props = {}

        self.transformers = config.transformers
        self._meta_data_settings = config.meta_data_settings
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
        
        # Create copies of the properties to avoid messing around with the originals.
        properties_copy = [copy.deepcopy(property) for property in self._properties]

        # Transform properties if transform function was provided.
        self._apply_transformations(properties_copy)

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

        s = self._dump(DumpInfo(
            self._type_name,
            properties_copy,
            self._indent,
            self._additional_props,
        ))

        # Make sure a string has been returned from _dump.
        if not isinstance(s, str):
            raise InvalidDumpTypeException()
        
        # Add meta data if required.
        s = self._add_meta_data(s)

        return self._add_newline(s)
    
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
    def _dump(self, info: DumpInfo) -> str:
        """
        Abstract method which must be implemented by the deriving class to create a type string.

        :param type_name:  Contains to required information to dump language specific code.
        :type type_name:   DumpInfo

        :return: Dumped type string.
        :rtype:  str
        """
        pass

    def _add_newline(self, s: str) -> str:
        """
        Adds a trailing newline if required.

        :param s: String to add the newline to.
        :type s:  str

        :return: Updated string.
        :rtype:  str
        """
        if s[-1] != '\n':
            s += '\n'
        return s
    
    def _add_meta_data(self, s: str) -> str:
        """
        Adds a meta data comment to the generated config string.

        :param s: Config string.
        :type s:  str

        :return: Updated config string.
        :rtype:  str
        """
        settings = self._meta_data_settings

        if settings:
            meta_data = {}

            if settings.user:
                meta_data['user'] = os.getlogin()
            if settings.date:
                meta_data['date'] = datetime.date.today().isoformat()
            if settings.time:
                meta_data['time'] = datetime.datetime.now().time().isoformat()
            if settings.version:
                meta_data['version'] = VERSION
            if settings.link:
                meta_data['link'] = 'https://pypi.org/project/ninja-bear/'

            items = meta_data.items()
            
            if len(items):
                s = self._add_newline(s) + '\n'
                s += self._add_newline(self._line_comment('------- metadata begin -------'))

                for attribute, value in items:
                    s += self._add_newline(
                        self._line_comment(f'{attribute}: {str(value)}')
                    )
                s += self._line_comment('------- metadata end ---------')

        return s

    def _set_type_name(self, name: str):
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
    
    def _apply_transformations(self, properties_copy: List[Property]) -> None:
        """
        Applies the user defined value transformation to each property value.

        :param properties_copy: Copy of all properties (to prevent modification of original).
        :type properties_copy:  List[Property]
        """
        if self.transformers:
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

                # Execute user defined Python scripts to transform properties.
                for transformer in self.transformers:
                    exec(transformer, None, local_variables)
                    
                    # Create new property from modified value.
                    properties_copy[i] = Property(
                        name=property.name,
                        value=local_variables[VALUE_KEY],
                        property_type=property.type,
                        hidden=property.hidden,
                        comment=property.comment,
                        namespace=property.namespace,
                    )
