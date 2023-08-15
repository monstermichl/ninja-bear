from typing import List

from ..generators.java_generator import JavaGenerator

from ..base.language_config_naming_conventions import LanguageConfigNamingConventions
from ..base.language_config_base import LanguageConfigBase
from ..base.language_type import LanguageType
from ..base.property import Property


class JavaConfig(LanguageConfigBase):
    """
    Java specific config. For more information about the config methods, refer to LanguageConfigBase.
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
            LanguageType.JAVA,
            'java',
            JavaGenerator,
            properties,
            indent,
            naming_conventions,
            additional_props,
        )

    def _allowed_file_name_pattern(self) -> str:
        return fr'^{self.generator.get_type_name()}$'
