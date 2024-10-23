from typing import Type

from .generator import Generator
from ninja_bear import LanguageConfigBase


class Config(LanguageConfigBase):
    """
    <name-upper> specific config. For more information about the config methods, refer to LanguageConfigBase.
    """

    def _file_extension(self) -> str:
        """
        Specifies which extension to use for the generated config file. For <name-upper> the
        file-extension '.<file-extension>' gets used.

        :return: Config file extension.
        :rtype:  str
        """
        return '<file-extension>'

    def _generator_type(self) -> Type[Generator]:
        """
        Specifies which GeneratorBase deriving class to use to actually generate the config file.
        In this case the Generator class from generator.py gets used. If you want to use a different
        Generator class or you want to rename the Generator class, make sure to update the return
        value accordingly.

        :return: GeneratorBase derivative class to generate the config file.
        :rtype:  Type[Generator]
        """
        return Generator

    def _allowed_file_naming_conventions(self) -> str:
        """
        Specifies the allowed file name pattern for the generated config file. This is necessary
        because some languages (e.g. Java) require the file to have a specific kind of naming format.

        :return: File naming regex.
        :rtype:  str
        """
        return r'.+'  # TODO: Probably needs to be changed by the implementer.
