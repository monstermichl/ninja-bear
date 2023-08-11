from os import path
import os
import pathlib
import shutil
from typing import List, Type
import unittest

from src.confluent import Orchestrator
from src.confluent.base.language_config import LanguageConfig
from src.confluent.base.language_type import LanguageType
from src.confluent.generators.java_generator import JavaGenerator
from src.confluent.generators.javascript_generator import JavascriptGenerator
from src.confluent.generators.typescript_generator import TypescriptGenerator
from src.confluent.generators.python_generator import PythonGenerator
from src.confluent.language_configs.java_config import JavaConfig
from src.confluent.language_configs.javascript_config import JavascriptConfig
from src.confluent.language_configs.typescript_config import TypescriptConfig
from src.confluent.language_configs.python_config import PythonConfig


class TestGenerator(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self._test_path = pathlib.Path(__file__).parent.resolve()
        self._test_config_path = path.join(self._test_path, '..', 'example/test-config.yaml')
        self._test_compare_files_path = path.join(self._test_path, 'compare_files')

    def test_read_config(self):
        orchestrator = Orchestrator.read_config(self._test_config_path)
        self._evaluate_configs(orchestrator.language_configs)

    def test_parse_config(self):
        with open(self._test_config_path, 'r') as f:
            content = f.read()
        orchestrator = Orchestrator.parse_config(content, 'test-config')
        self._evaluate_configs(orchestrator.language_configs)

    def test_run_generators(self):
        orchestrator = Orchestrator.read_config(self._test_config_path)

        for config in orchestrator.language_configs:
            compare_file_path = path.join(
                self._test_compare_files_path,
                f'{config.config_info.file_name_full}'
            )
            
            with open(compare_file_path, 'r') as f:
                content = f.read()
            self.assertEqual(config.dump(), content)

    def test_write_configs(self):
        OUTPUT_DIR = path.join(self._test_path, 'test_output')
        orchestrator = Orchestrator.read_config(self._test_config_path)

        if not os.path.isdir(OUTPUT_DIR):
            os.mkdir(OUTPUT_DIR)
        
        # Write all configs to the output folder.
        orchestrator.write(OUTPUT_DIR)

        # Collect the output file names.
        files = os.listdir(OUTPUT_DIR)

        # Cleanup output directory.
        shutil.rmtree(OUTPUT_DIR)

        # Compare files.
        for config in orchestrator.language_configs:
            self.assertIn(config.config_info.file_name_full, files)

    def _evaluate_configs(self, configs: List[LanguageConfig]):
        self.assertIsNotNone(configs)
        self.assertIsInstance(configs, list)
        self.assertEqual(len(configs), 4)  # Don't forget to update when adding a new language to test-config.yaml.

        # Check Java config.
        self._evaluate_java_properties(configs[0], 'TestConfig')

        # Check JavaScript config.
        self._evaluate_javascript_properties(configs[1], 'TEST_CONFIG')

        # Check TypeScript config.
        self._evaluate_typescript_properties(configs[2], 'test-config')

        # Check Python config.
        self._evaluate_python_properties(configs[3], 'test_config')

    def _evaluate_java_properties(self, config: JavaConfig, name: str):
        self._evaluate_common_properties(config, 'java', name, LanguageType.JAVA, JavaGenerator)
        self.assertEqual(config.generator.package, 'my.test.package')

    def _evaluate_javascript_properties(self, config: JavascriptConfig, name: str):
        self._evaluate_common_properties(config, 'js', name, LanguageType.JAVASCRIPT, JavascriptGenerator)

    def _evaluate_typescript_properties(self, config: TypescriptConfig, name: str):
        self._evaluate_common_properties(config, 'ts', name, LanguageType.TYPESCRIPT, TypescriptGenerator)

    def _evaluate_python_properties(self, config: PythonConfig, name: str):
        self._evaluate_common_properties(config, 'py', name, LanguageType.PYTHON, PythonGenerator)

    def _evaluate_common_properties(
        self,
        config: LanguageConfig,
        extension: str,
        name: str,
        type: LanguageType,
        generator_type: Type
    ):
        self.assertEqual(config.config_info.file_extension, extension)
        self.assertEqual(config.config_info.file_name, name)
        self.assertEqual(config.language_type, type)
        self.assertEqual(config.generator.__class__, generator_type)
