from __future__ import annotations
from abc import ABC, abstractmethod
import re
from typing import List, Type

from .configuration_base import _DEFAULT_INDENT
from .generator_base import GeneratorBase
from .distributor_base import DistributorBase
from .language_config_configuration import LanguageConfigConfiguration
from .language_config_naming_conventions import LanguageConfigNamingConventions
from .name_converter import NamingConventionType
from .config_file_info import ConfigFileInfo
from .name_converter import NameConverter
from .property import Property
from .meta_data_settings import MetaDataSettings


class InvalidFileNameException(Exception):
    def __init__(self, file_name: str, pattern: str, class_type: type):
        type_name = class_type.__name__

        super().__init__(
            f'The file name "{file_name}" does not conform to the validation pattern "{pattern}" of {type_name} '
            'as it might be problematic to import the module later on. The output-filename convention can be '
            'specified using the "file_naming" property.'
        )


class LanguageConfigBase(ABC):
    """
    Abstract class which serves as the base for all language specific config classes. The LanguageConfigBase holds all
    required information (language type, naming convention, generator, ...) to generate a config file.
    """

    def __init__(
        self,
        input_path: str,
        properties: List[Property],
        indent: int = _DEFAULT_INDENT,
        transformers: List[str] = None,
        naming_conventions: LanguageConfigNamingConventions = None,
        distributors: List[DistributorBase] = None,
        meta_data_settings: MetaDataSettings = None,
        additional_props = {},
    ):
        """
        Constructor

        :param input_path:         Language input config path.
        :type input_path:          str
        :param properties:         List of properties.
        :type properties:          List[Property]
        :param indent:             Property indent for the generated config, defaults to _DEFAULT_INDENT
        :type indent:              int, optional
        :param transformers:       Python functions which can transform the provided value, defaults to None
        :type transformers:        List[str], optional
        :param naming_conventions: Naming convention to use for the generated config file, defaults to None
        :type naming_conventions:  LanguageConfigNamingConventions, optional
        :param distributors:       List of distributors, defaults to None
        :type distributors:        List[DistributorBase], optional
        :param additional_props:   All props that might by needed by the derivating class, defaults to {}
        :type additional_props:    dict, optional
        """
        config = LanguageConfigConfiguration(
            input_path,
            file_extension=self._file_extension(),
            generator_type=self._generator_type(),
            indent=indent,
            transformers=transformers,
            naming_conventions=naming_conventions,
            distributors=distributors,
            meta_data_settings=meta_data_settings,
        )

        # Make sure, config is valid.
        config.validate()

        self.generator = config.generator_type(
            config.get_generator_config(),
            properties,
            additional_props,
        )
        file_naming_convention = config.naming_conventions.file_naming_convention
        file_naming_convention = file_naming_convention \
            if file_naming_convention else self._default_file_naming_convention()
        
        self.input_path = config.input_path
        self.config_info = ConfigFileInfo(
            # Convert config file name according to naming convention if a convention was provided. Otherwise, just use
            # the config name directly.
            NameConverter.convert(
                config.config_name,
                file_naming_convention if file_naming_convention else NamingConventionType.SNAKE_CASE,
            ),
            config.file_extension,
        )
        self.distributors = distributors if distributors else []

        # Check output file naming.
        self._check_file_name()

    def dump(self) -> str:
        """
        Generates a config file string.

        :return: Config file string.
        :rtype:  str
        """
        return self.generator.dump()
    
    def write(self, path: str = ''):
        """
        Generates a config file string and writes the config file to the provided directory.

        :param path: Directory to write the file to, defaults to ''
        :type path:  str, optional

        :return:     The current LanguageConfigBase instance.
        :rtype:      LanguageConfigBase
        """
        path = path.rstrip('/').rstrip('\\')  # Strip right-side slashes.
        path = f'{path}/{self.config_info.file_name_full}'

        with open(path, 'w') as f:
            f.write(self.dump())
        return self
    
    def distribute(self):
        """
        Distributes the generated config file via the specified distributors.

        :return: The current LanguageConfigBase instance.
        :rtype:  LanguageConfigBase
        """
        data = self.dump()

        [distributor.distribute(
            self.config_info.file_name_full,
            data,
            self.input_path,
        ) for distributor in self.distributors]            
        return self

    @abstractmethod
    def _file_extension(self) -> str:
        pass

    @abstractmethod
    def _generator_type(self) -> Type[GeneratorBase]:
        pass

    @abstractmethod
    def _default_file_naming_convention(self) -> NamingConventionType:
        pass

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
        """
        Checks if the config file name matches the pattern defined by the deriving class.

        :raises InvalidFileNameException: Thrown if the file name is not valid.
        """
        pattern = self._allowed_file_name_pattern()

        if not re.match(pattern, self.config_info.file_name):
            raise InvalidFileNameException(self.config_info.file_name, pattern, type(self))
