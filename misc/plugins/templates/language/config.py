from typing import Type

from .generator import Generator
from ninja_bear import LanguageConfigBase


class Config(LanguageConfigBase):
    """
    <name-upper> specific config. For more information about the config methods, refer to LanguageConfigBase.
    """

    def _file_extension(self) -> str:
        return '<file-extension>'

    def _generator_type(self) -> Type[Generator]:
        return Generator  # TODO: Probably needs to be changed by the implementer.

    def _allowed_file_name_pattern(self) -> str:
        return r'.+'  # TODO: Probably needs to be changed by the implementer.
