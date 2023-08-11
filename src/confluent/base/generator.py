from typing import List

from .language_config import LanguageConfig
from .config import Config

class Generator:

    @staticmethod
    def read_config(path: str) -> List[LanguageConfig]:
        """
        Reads the provided YAML configuration file and generates a list of language configurations.

        :param path: Path to load the YAML file from (see example/test-config.yaml for configuration details).
        :type path:  str

        :return: List of language configurations.
        :rtype:  List[LanguageConfig]
        """
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
        """
        Parses the provided YAML configuration string and generates a list of language configurations. 

        :param config:      YAML configuration string (see example/test-config.yaml for configuration details).
        :type config:       str
        :param config_name: Name of the generated type and config. HINT: This acts more like a template for the
                            type name than the real name as some conventions must be met and therefore the default
                            convention specified by the deriving class of GeneratorBase will be used if no naming
                            convention for the type name was provided (see
                            GeneratorBase._default_type_naming_convention).
        :type config_name:  str

        :return: List of language configurations.
        :rtype:  List[LanguageConfig]
        """
        return Config.parse(config, config_name)
