from os import path
import pathlib
import re
import unittest

from ninja_bear import Orchestrator
from ninja_bear.base.generator_configuration import GeneratorConfiguration
from src.<module-folder>.generator import Generator


class Test(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self._test_path = pathlib.Path(__file__).parent.resolve()
        self._test_config_path = path.join(self._test_path, '..', 'example/test-config.yaml')
        self._test_compare_files_path = path.join(self._test_path, 'compare_files')

    def test_run_generators(self):
        orchestrator = Orchestrator.read_config(self._test_config_path)
        language_configs = orchestrator.language_configs

        self.assertEqual(len(language_configs), 1)

        language_config = language_configs[0]
        config_generator = language_config.generator
        local_generator = Generator(
            GeneratorConfiguration(
                indent=config_generator._indent,
                transformers=config_generator.transformers,
                naming_conventions=config_generator._naming_conventions,
                type_name=config_generator._type_name
            ),
            properties=config_generator._properties,
            additional_props=config_generator._additional_props,
        )

        compare_file_path = path.join(
            self._test_compare_files_path,
            f'{language_config.config_info.file_name_full}'
        )
        
        with open(compare_file_path, 'r') as f:
            content = f.read()

        original_max_diff = self.maxDiff
        self.maxDiff = None
        self.assertEqual(local_generator.dump()), content)
        self.maxDiff = original_max_diff
