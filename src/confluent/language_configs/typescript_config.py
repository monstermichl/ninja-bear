from typing import List

from ..generators.typescript_generator import TypescriptGenerator

from ..base.language_config import LanguageConfig
from ..base.name_converter import NamingConventionType
from ..base.language_type import LanguageType
from ..base.property import Property


class TypescriptConfig(LanguageConfig):
    def __init__(
        self,
        config_name: str,
        file_naming_convention: NamingConventionType,
        properties: List[Property],
        indent: int = None,
        additional_props = {},
    ):
        super().__init__(
            config_name,
            LanguageType.TYPESCRIPT,
            file_naming_convention,
            'ts',
            TypescriptGenerator,
            properties,
            indent,
            additional_props,
        )

    def _default_naming_convention(self) -> NamingConventionType:
        return NamingConventionType.KEBAP_CASE
