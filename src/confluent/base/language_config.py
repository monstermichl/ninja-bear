from abc import ABC, abstractmethod
from typing import List, Type

from .language_config_naming_conventions import LanguageConfigNamingConventions
from .config_file_info import ConfigFileInfo
from .name_converter import NameConverter, NamingConventionType
from .language_type import LanguageType
from .property import Property
from .generator_base import GeneratorBase


class NoConfigNameProvidedException(Exception):
    def __init__(self):
        super().__init__('No config name has been provided')


class LanguageConfig(ABC):
    """
    Abstract class which serves as the base for all language specific config classes. The LanguageConfig holds all
    required information (language type, naming convention, generator, ...) to generate a config file.
    """

    def __init__(
        self,
        config_name: str,
        language_type: LanguageType,
        file_extension: str,
        generator: Type[GeneratorBase],
        properties: List[Property],
        indent: int = None,
        naming_conventions: LanguageConfigNamingConventions = None,
        additional_props = {},
    ):
        """
        Constructor

        :param config_name:               Name of the generated class and config. HINT: This acts more like a template
                                          than the real name as some conventions must be met and therefore the name
                                          might be changed in terms of casing (see also GeneratorBase
                                          and NameConverter).
        :type config_name:                str
        :param language_type:             Which language type is this config for.
        :type language_type:              LanguageType
        :param file_extension:            Which file extension to use for the output file.
        :type file_extension:             str
        :param generator:                 Which generator to use to generate the config.
        :type generator:                  Type[GeneratorBase]
        :param properties:                Which properties to generate.
        :type properties:                 List[Property]
        :param indent:                    How much leading whitespace indent to use for each property, defaults to None
        :type indent:                     int, optional
        :param naming_conventions:        Specifies which case convention to use for the properties. If not provided,
                                          the name as specified will be used. Defaults to None
        :type GeneratorNamingConventions: LanguageConfigNamingConventions, optional
        :param additional_props:          Additional props which might be required by the deriving generator class,
                                          defaults to {}
        :type additional_props:           dict, optional

        :raises NoConfigNameProvidedException: Raised if no config name has been provided.
        """
        if not config_name:
            raise NoConfigNameProvidedException()
        
        # Make sure that the naming conventions are available.
        if not naming_conventions:
            naming_conventions = LanguageConfigNamingConventions()
        
        # Make sure that the file-naming convention is set to default if not provided.
        if not naming_conventions.file_naming_convention:
            naming_conventions.file_naming_convention = self._default_naming_convention()
        
        self.generator = generator(
            config_name,
            properties,
            indent,
            naming_conventions,
            additional_props,
        )
        self.config_info = ConfigFileInfo(
            NameConverter.convert(config_name, naming_conventions.file_naming_convention),
            file_extension,
        )
        self.language_type = language_type

    def dump(self) -> str:
        """
        Generates a config file string.

        :return: Config file string.
        :rtype:  str
        """
        return self.generator.dump()
    
    @abstractmethod
    def _default_naming_convention(self) -> NamingConventionType:
        """
        Abstract method which must be implemented by the deriving class that returns the default file naming convention.

        :return: Default file naming convention.
        :rtype:  NamingConventionType
        """
        pass
