from __future__ import annotations
from abc import ABC, abstractmethod
import re
from typing import List

from .language_config_configuration import LanguageConfigConfiguration
from .config_file_info import ConfigFileInfo
from .name_converter import NameConverter
from .property import Property


class InvalidFileNameException(Exception):
    def __init__(self, file_name: str, pattern: str):
        super().__init__(f'The file name "{file_name}" does not conform to the validation pattern "{pattern}"')


class LanguageConfigBase(ABC):
    """
    Abstract class which serves as the base for all language specific config classes. The LanguageConfigBase holds all
    required information (language type, naming convention, generator, ...) to generate a config file.
    """

    def __init__(
        self,
        config: LanguageConfigConfiguration,
        properties: List[Property],
        additional_props = {},
    ):
        """
        Constructor

        :param config:           Language config configuration.
        :type config:            LanguageConfigConfiguration
        :param properties:       Which properties to generate.
        :type properties:        List[Property]
        :param additional_props: Additional props which might be required by the deriving generator class,
                                 defaults to {}
        :type additional_props:  dict, optional
        """

        # Make sure, config is valid.
        config.validate()

        self.generator = config.generator_type(
            config.get_generator_config(),
            properties,
            additional_props,
        )
        self.config_info = ConfigFileInfo(
            # Convert config file name according to naming convention if a convention was provided. Otherwise, just use
            # the config name directly.
            NameConverter.convert(config.config_name, config.naming_conventions.file_naming_convention) if
                config.naming_conventions.file_naming_convention else
                config.config_name,

            config.file_extension,
        )
        self.language_type = config.language_type

        # Check output file naming.
        self._check_file_name()

    def dump(self) -> str:
        """
        Generates a config file string.

        :return: Config file string.
        :rtype:  str
        """
        return self.generator.dump()
    
    def write(self, path: str = '') -> LanguageConfigBase:
        path = path.rstrip('/').rstrip('\\')  # Strip right-side slashes.
        path = f'{path}/{self.config_info.file_name_full}'

        with open(path, 'w') as f:
            f.write(self.dump())
        return self
    
    @abstractmethod
    def _allowed_file_name_pattern(self) -> str:
        """
        Abstract method which must be implemented by the deriving class to provide a RegEx string which describes which
        file name patterns are allowed for the output file name (without extension).

        :return: Allowed file name pattern.
        :rtype:  str
        """
        pass

    def _check_file_name(self) -> None:
        pattern = self._allowed_file_name_pattern()

        if not re.match(pattern, self.config_info.file_name):
            raise InvalidFileNameException(self.config_info.file_name, pattern)
