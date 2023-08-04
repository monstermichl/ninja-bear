from abc import abstractmethod
from typing import List, Self, Type

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
    ) -> Self:
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
        self.config_name = NameConverter.convert(config_name, file_naming_convention)
        self.config_extension = file_extension
        self.language_type = language_type

    def dump(self) -> str:
        return self.generator.dump()
    
    @abstractmethod
    def _default_naming_convention(self) -> NamingConventionType:
        pass
