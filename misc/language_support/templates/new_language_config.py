from typing import List

from ..generators.<language-generator-file> import <language-generator>  # TODO: Update according to the new language.

from ..base.language_config_naming_conventions import LanguageConfigNamingConventions
from ..base.language_config import LanguageConfig
from ..base.language_type import LanguageType
from ..base.property import Property


class NewLanguageConfig(LanguageConfig):
    """
    NewLanguage specific config. For more information about the config methods, refer to LanguageConfig.
    """

    def __init__(
        self,
        config_name: str,
        properties: List[Property],
        indent: int = None,
        naming_conventions: LanguageConfigNamingConventions = None,
        additional_props = {},
    ):
        super().__init__(
            config_name,
            LanguageType.<language-type>,  # TODO: Update according to the new language.
            '<language-file-extension>',  # TODO: Update according to the new language.
            <lanuage-generator>,  # TODO: Update according to the new language.
            properties,
            indent,
            naming_conventions,
            additional_props,
        )
