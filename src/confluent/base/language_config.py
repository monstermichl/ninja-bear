from abc import abstractmethod
from typing import List, Type

from .config_info import ConfigInfo
from .name_converter import NameConverter, NamingConventionType
from .language_type import LanguageType
from .property import Property
from .generator_base import GeneratorBase


class LanguageConfig:
    def __init__(
        self,
        config_name: str,
        language_type: LanguageType,
        file_naming_convention: NamingConventionType,
        file_extension: str,
        generator: Type[GeneratorBase],
        properties: List[Property],
        indent: int = None,
        additional_props = {},
    ):
        if not config_name:
            raise Exception('No config name provided')
        
        if not file_naming_convention:
            file_naming_convention = self._default_naming_convention()
        
        self.generator = generator(
            config_name,
            properties,
            indent,
            additional_props,
        )
        self.config_info = ConfigInfo(
            NameConverter.convert(config_name, file_naming_convention),
            file_extension,
        )
        self.language_type = language_type

    def dump(self) -> str:
        return self.generator.dump()
    
    @abstractmethod
    def _default_naming_convention(self) -> NamingConventionType:
        pass
