from typing import List

from ..generators.python_generator import PythonGenerator

from ..base.language_config_naming_conventions import LanguageConfigNamingConventions
from ..base.language_config import LanguageConfig
from ..base.name_converter import NamingConventionType
from ..base.language_type import LanguageType
from ..base.property import Property


class PythonConfig(LanguageConfig):
    """
    Python specific config. For more information about the config methods, refer to LanguageConfig.
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
            LanguageType.PYTHON,
            'py',
            PythonGenerator,
            properties,
            indent,
            naming_conventions,
            additional_props,
        )

    def _default_naming_convention(self) -> NamingConventionType:
        return NamingConventionType.SNAKE_CASE
