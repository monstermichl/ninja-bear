from __future__ import annotations
from typing import List

from .language_config import LanguageConfig
from .config import Config

class Arranger:

    def __init__(self, language_configs: List[LanguageConfig]):
        # Make sure the configs-list is available.
        if not language_configs:
            language_configs = []

        self.language_configs = language_configs

    def dump(self) -> List[str]:
        """
        Dumps all language configs into a list of strings.

        :return: List of config strings.
        :rtype:  List[str]
        """
        return [config.dump() for config in self.language_configs]
    
    def write(self, path: str = '') -> Arranger:
        """
        Writes all language configs to the specified output path.

        :param path: Path to write the configs to (the directory must exist), defaults to ''
        :type path:  str, optional

        :return: The current Arranger instance.
        :rtype:  Arranger
        """
        [config.write(path) for config in self.language_configs]
        return self

    @staticmethod
    def read_config(path: str) -> Arranger:
        """
        Reads the provided YAML configuration file and generates a list of language configurations.

        :param path: Path to load the YAML file from (see example/test-config.yaml for configuration details).
        :type path:  str

        :return: Arranger instance.
        :rtype:  Arranger
        """
        with open(path, 'r') as f:
            content = f.read()

        # Prepare config name.
        last_part = path.replace(r'\\', '/').split('/')[-1]

        if '.' in last_part:
            config_name = '.'.join(last_part.split('.')[0:-1])
        else:
            config_name = last_part
        return Arranger.parse_config(content, config_name)

    @staticmethod
    def parse_config(config: str, config_name: str) -> Arranger:
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

        :return: Arranger instance.
        :rtype:  Arranger
        """
        return Arranger(Config.parse(config, config_name))
