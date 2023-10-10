from typing import Type

from ..generators.<language-generator-file> import <language-generator>  # TODO: Update according to the new language.

from ..base.generator_base import GeneratorBase
from ..base.language_config_base import LanguageConfigBase
from ..base.language_type import LanguageType


class NewLanguageConfig(LanguageConfigBase):
    """
    NewLanguage specific config. For more information about the config methods, refer to LanguageConfigBase.
    """

    def _language_type(self) -> LanguageType:
        return LanguageType.<language-type>  # TODO: Update according to the new language.

    def _file_extension(self) -> str:
        return '<language-file-extension>'  # TODO: Update according to the new language.

    def _generator_type(self) -> Type[GeneratorBase]:
        return <lanuage-generator>  # TODO: Update according to the new language.

    def _allowed_file_name_pattern(self) -> str:
        return r'.+'  # TODO: Update according to the new language.
