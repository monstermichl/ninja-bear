from os import path
import pathlib
from typing import List, Type
import unittest

from src import ConfigGenerator
from src.base.language_config import LanguageConfig
from src.base.language_type import LanguageType
from src.generators.java_generator import JavaGenerator
from src.generators.typescript_generator import TypescriptGenerator
from src.language_configs.java_config import JavaConfig
from src.language_configs.typescript_config import TypescriptConfig

class TestGenerator(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self._test_path = pathlib.Path(__file__).parent.resolve()
        self._test_config_path = path.join(self._test_path, '..', 'example/test-config.yaml')

    def test_read_config(self):
        configs = ConfigGenerator.read_config(self._test_config_path)
        self._evaluate_configs(configs)

    def test_parse_config(self):
        with open(self._test_config_path, 'r') as f:
            content = f.read()
        configs = ConfigGenerator.parse_config(content, 'TestConfig')
        self._evaluate_configs(configs)

    def _evaluate_configs(self, configs: List[LanguageConfig]):
        self.assertIsNotNone(configs)
        self.assertIsInstance(configs, list)
        self.assertEqual(len(configs), 2)

        # Check Java config.
        self._evaluate_java_properties(configs[0], 'TestConfig')

        # Check Typescript config.
        self._evaluate_typescript_properties(configs[1], 'test-config')

    def _evaluate_java_properties(self, config: JavaConfig, name: str):
        self._evaluate_common_properties(config, 'java', name, LanguageType.JAVA, JavaGenerator)
        # TODO: Add package evaluation.

    def _evaluate_typescript_properties(self, config: TypescriptConfig, name: str):
        self._evaluate_common_properties(config, 'ts', name, LanguageType.TYPESCRIPT, TypescriptGenerator)

    def _evaluate_common_properties(
        self,
        config: LanguageConfig,
        extension: str,
        name: str,
        type: LanguageType,
        generator_class: Type
    ):
        self.assertEqual(config.config_extension, extension)
        self.assertEqual(config.config_name, name)
        self.assertEqual(config.language_type, type)
        self.assertEqual(config.generator.__class__, generator_class)
