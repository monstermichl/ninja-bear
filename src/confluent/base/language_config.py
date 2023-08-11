from abc import ABC
from typing import List, Type

from .language_config_naming_conventions import LanguageConfigNamingConventions
from .config_file_info import ConfigFileInfo
from .name_converter import NameConverter
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

        :param config_name:               Name of the generated type and config. HINT: This acts more like a template
                                          for the type name than the real name as some conventions must be met and
                                          therefore the default convention specified by the deriving class of
                                          GeneratorBase will be used if no naming convention for the type name
                                          was provided (see GeneratorBase._default_type_naming_convention).
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
        
        self.generator = generator(
            config_name,
            properties,
            indent,
            naming_conventions,
            additional_props,
        )
        self.config_info = ConfigFileInfo(
            # Convert config file name according to naming convention if a convention was provided. Otherwise, just use
            # the config name directly.
            NameConverter.convert(config_name, naming_conventions.file_naming_convention) if
                naming_conventions.file_naming_convention else
                config_name,

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
