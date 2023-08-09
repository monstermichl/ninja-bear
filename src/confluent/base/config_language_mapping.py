from __future__ import annotations
from typing import List

from ..language_configs.java_config import JavaConfig
from ..language_configs.javascript_config import JavascriptConfig
from ..language_configs.typescript_config import TypescriptConfig

from .language_config import LanguageConfig
from .language_type import LanguageType


class ConfigLanguageMapping:
    def __init__(self, name: str, type: LanguageType, config_type: LanguageConfig.__class__):
        self.name = name
        self.type = type
        self.config_type = config_type

    @staticmethod
    def get_mappings() -> List[ConfigLanguageMapping]:
        return [
            ConfigLanguageMapping('java', LanguageType.JAVA, JavaConfig),
            ConfigLanguageMapping('javascript', LanguageType.JAVASCRIPT, JavascriptConfig),
            ConfigLanguageMapping('typescript', LanguageType.TYPESCRIPT, TypescriptConfig),
        ]
