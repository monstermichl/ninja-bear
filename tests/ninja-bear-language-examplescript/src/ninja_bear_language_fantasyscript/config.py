from typing import Type

from .generator import Generator
from ninja_bear import LanguageConfigBase


class Config(LanguageConfigBase):
    """
    ExampleScript specific config. For more information about the config methods, refer to LanguageConfigBase.
    """

    def _file_extension(self) -> str:
        return 'es'

    def _generator_type(self) -> Type[Generator]:
        return Generator

    def _allowed_file_name_pattern(self) -> str:
        return r'.+'
