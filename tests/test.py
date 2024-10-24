from os import path
import os
import pathlib
import re
import shutil
from typing import Dict, List, Type
import unittest

from src.ninja_bear import GeneratorBase, PropertyType, NamingConventionType, DumpInfo, DistributeInfo, Plugin
from src.ninja_bear.base.orchestrator import Orchestrator
from src.ninja_bear.base.generator_configuration import GeneratorConfiguration
from src.ninja_bear.base.language_config_base import LanguageConfigBase
from src.ninja_bear.base.distributor_base import DistributorBase
from src.ninja_bear.base.distributor_credentials import DistributorCredentials


_NINJA_BEAR_REFERENCE_REGEX = r'Generated with ninja-bear v\d+\.\d+\.\d+'
_COMPARE_FILE_CONTENT = """
struct TestConfig:
    boolean myBoolean = true
    int myInteger = 142
    float myFloat = 322.0
    float myCombinedFloat = 45724.0
    double myDouble = 233.9
    regex myRegex = /Test Reg(E|e)x/ -- Just another RegEx.
    string mySubstitutedString = 'Sometimes I just want to scream Hello Mars!'
    string myCombinedString = 'I am telling you that this string got included from test-include.yaml.'
"""


class ExampleScriptGenerator(GeneratorBase):
    """
    ExampleScript specific generator. For more information about the generator methods, refer to GeneratorBase.
    """

    def _default_type_naming_convention(self) -> NamingConventionType:
        return NamingConventionType.PASCAL_CASE
    
    def _line_comment(self, string: str) -> str:
        return f'-- {string}'
    
    def _dump(self, info: DumpInfo) -> str:
        code = f'struct {info.type_name}:\n'

        for property in info.properties:
            type = property.type
            value = property.value

            if type == PropertyType.BOOL:
                type_string = 'boolean'
                value = 'true' if value else 'false'
            elif type == PropertyType.INT:
                type_string = 'int'
            elif type == PropertyType.FLOAT:
                type_string = 'float'
            elif type == PropertyType.DOUBLE:
                type_string = 'double'
            elif type == PropertyType.STRING:
                type_string = 'string'
                value = f'\'{value}\''
            elif type == PropertyType.REGEX:
                type_string = 'regex'
                value = f'/{value}/'

            comment = f' {self._line_comment(property.comment)}' if property.comment else ''
            code += f'{" " * info.indent}{type_string} {property.name} = {value}{comment}\n'

        return code


class ExampleScriptConfig(LanguageConfigBase):
    """
    ExampleScript specific config. For more information about the config methods, refer to LanguageConfigBase.
    """

    def _file_extension(self) -> str:
        return 'es'

    def _generator_type(self) -> Type[ExampleScriptGenerator]:
        return ExampleScriptGenerator
    
    def _default_file_naming_convention(self) -> NamingConventionType:
        return NamingConventionType.KEBAP_CASE

    def _allowed_file_name_pattern(self) -> str:
        return r'.+'
    

class ExampleDistributor(DistributorBase):
    def __init__(self, config: Dict, credentials: DistributorCredentials=None) -> DistributorBase:
        super().__init__(config, credentials)

    def _distribute(self, info: DistributeInfo):
        return self


class Test(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self._test_path = pathlib.Path(__file__).parent.resolve()
        self._test_config_path = path.join(self._test_path, '..', 'example/test-config.yaml')
        self._plugins = [
            Plugin('examplescript', ExampleScriptConfig),
            Plugin('exampledistributor', ExampleDistributor),
        ]

    def test_read_config(self):
        orchestrator = Orchestrator.read_config(self._test_config_path, plugins=self._plugins)
        self._evaluate_configs(orchestrator.language_configs)

    def test_parse_config(self):
        TEST_INCLUDE = 'test-include.yaml'

        with open(self._test_config_path, 'r') as f:
            content = f.read().replace(TEST_INCLUDE, os.path.join(os.getcwd(), 'example', TEST_INCLUDE))
        orchestrator = Orchestrator.parse_config(content, 'test-config', plugins=self._plugins)

        self._evaluate_configs(orchestrator.language_configs)

    def test_run_generators(self):
        orchestrator = Orchestrator.read_config(self._test_config_path, plugins=self._plugins)
        language_configs = orchestrator.language_configs

        self.assertEqual(len(language_configs), 1)

        language_config = language_configs[0]
        config_generator = language_config.generator
        local_generator = ExampleScriptGenerator(
            GeneratorConfiguration(
                indent=config_generator._indent,
                transformers=config_generator.transformers,
                naming_conventions=config_generator._naming_conventions,
                type_name=config_generator._type_name
            ),
            properties=config_generator._properties,
            additional_props=config_generator._additional_props,
        )

        original_max_diff = self.maxDiff
        self.maxDiff = None

        self.assertEqual(
            # Remove versions to keep tests working if version changed.
            re.sub(_NINJA_BEAR_REFERENCE_REGEX, '', local_generator.dump().strip()), 
            re.sub(_NINJA_BEAR_REFERENCE_REGEX, '', _COMPARE_FILE_CONTENT.strip()),
        )
        self.maxDiff = original_max_diff

    def test_write_configs(self):
        OUTPUT_DIR = path.join(self._test_path, 'test_output')
        orchestrator = Orchestrator.read_config(self._test_config_path, plugins=self._plugins)

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

    def test_distribution(self):
        # Get secret from environment variables.
        credential = DistributorCredentials('example-alias', None, 'password')
        orchestrator = Orchestrator.read_config(self._test_config_path, [credential], plugins=self._plugins)

        self._evaluate_configs(orchestrator.language_configs)
        orchestrator.distribute()

    def _evaluate_configs(self, configs: List[LanguageConfigBase]):
        self.assertEqual(len(configs), 1)
        self._evaluate_config(configs[0])

    def _evaluate_config(self, config: LanguageConfigBase):
        self.assertIsNotNone(config)
        self.assertEqual(config.config_info.file_extension, 'es')
        self.assertEqual(config.config_info.file_name, 'TestConfig')

    def _evaluate_common_properties(
        self,
        config: LanguageConfigBase,
        extension: str,
        name: str,
    ):
        self.assertEqual(config.config_info.file_extension, extension)
        self.assertEqual(config.config_info.file_name, name)
