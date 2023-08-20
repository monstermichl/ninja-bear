from typing import List

from ..generators.c_generator import CGenerator

from ..base.language_config_configuration import LanguageConfigConfiguration
from ..base.language_config_naming_conventions import LanguageConfigNamingConventions
from ..base.language_config_base import LanguageConfigBase
from ..base.language_type import LanguageType
from ..base.property import Property


class CConfig(LanguageConfigBase):
    """
    C specific config. For more information about the config methods, refer to LanguageConfigBase.
    """

    def __init__(
        self,
        config_name: str,
        properties: List[Property],
        indent: int,
        transform: str,
        naming_conventions: LanguageConfigNamingConventions,
        additional_props = {},
    ):
        super().__init__(
            LanguageConfigConfiguration(
                config_name,
                LanguageType.C,
                'h',
                CGenerator,
                indent,
                transform,
                naming_conventions,
            ),
            properties,
            additional_props,
        )

    def _allowed_file_name_pattern(self) -> str:
        return r'^\w+$'