from typing import List

from .language_config import LanguageConfig
from .config import Config

class ConfigGenerator:
    @staticmethod
    def read_config(path: str) -> List[LanguageConfig]:
        with open(path, 'r') as f:
            content = f.read()

        # Prepare config name.
        last_part = path.replace(r'\\', '/').split('/')[-1]

        if '.' in last_part:
            config_name = '.'.join(last_part.split('.')[0:-1])
        else:
            config_name = last_part
        return Config.parse(content, config_name)

    @staticmethod
    def parse_config(config: str, config_name: str) -> List[LanguageConfig]:
        return Config.parse(config, config_name)
