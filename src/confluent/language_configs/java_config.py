from typing import List

from ..generators.java_generator import JavaGenerator

from ..base.language_config import LanguageConfig
from ..base.name_converter import NamingConventionType
from ..base.language_type import LanguageType
from ..base.property import Property


class JavaConfig(LanguageConfig):
    """
    Java specific config. For more information about the config methods, refer to LanguageConfig.
    """

    def __init__(
        self,
        config_name: str,
        file_naming_convention: NamingConventionType,
        properties: List[Property],
        indent: int = None,
        property_naming_convention: NamingConventionType = None,
        additional_props = {},
    ):
        super().__init__(
            config_name,
            LanguageType.JAVA,
            file_naming_convention,
            'java',
            JavaGenerator,
            properties,
            indent,
            property_naming_convention,
            additional_props,
        )

    def _default_naming_convention(self) -> NamingConventionType:
        return NamingConventionType.PASCAL_CASE
