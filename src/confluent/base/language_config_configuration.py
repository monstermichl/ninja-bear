from typing import Type

from .configuration_base import _DEFAULT_INDENT, ConfigurationBase
from .language_type import LanguageType
from .language_config_naming_conventions import LanguageConfigNamingConventions
from .generator_base import GeneratorBase
from .generator_configuration import GeneratorConfiguration


class NoConfigNameProvidedException(Exception):
    def __init__(self):
        super().__init__('No config name has been provided')


class LanguageConfigConfiguration(ConfigurationBase):
    """
    Encapsulates the configuration properties used by the LanguageConfigBase class.
    """

    def __init__(
        self,
        config_name: str,
        language_type: LanguageType,
        file_extension: str,
        generator_type: Type[GeneratorBase],
        indent: int = _DEFAULT_INDENT,
        transform: str = None,
        naming_conventions: LanguageConfigNamingConventions = None,
    ) -> None:
        super().__init__()

        self.config_name = config_name
        self.language_type = language_type
        self.file_extension = file_extension
        self.generator_type = generator_type
        self.indent = indent
        self.transform = transform
        self.naming_conventions = naming_conventions

    def validate(self):
        if not self.config_name:
            raise NoConfigNameProvidedException()
        
        # Make sure that the naming conventions are available.
        if not self.naming_conventions:
            self.naming_conventions = LanguageConfigNamingConventions()

    def get_generator_config(self) -> GeneratorConfiguration:
        generator_config = GeneratorConfiguration()

        generator_config.type_name = self.config_name
        generator_config.indent = self.indent
        generator_config.transform = self.transform
        generator_config.naming_conventions = self.naming_conventions

        return generator_config
