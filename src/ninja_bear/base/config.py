from __future__ import annotations
import os
import re
from typing import Dict, List, Tuple, Type

import yaml
from schema import Schema, Use, Optional, Or

from .plugin_loader import Plugin, PluginLoader, PluginType
from .config_language_mapping import ConfigLanguageMapping
from .name_converter import NamingConventionType
from .property import Property
from .property_type import PropertyType
from .language_type import LanguageType
from .language_config_base import LanguageConfigBase
from .language_config_naming_conventions import LanguageConfigNamingConventions
from .distributor_base import DistributorBase, DistributorCredentials

# Main keys.
_KEY_INCLUDES = 'includes'
_KEY_LANGUAGES = 'languages'
_KEY_PROPERTIES = 'properties'
_KEY_IGNORE = 'ignore'

# Include keys.
_INCLUDE_KEY_PATH = 'path'
_INCLUDE_KEY_AS = 'as'

# Language keys.
_LANGUAGE_KEY_LANGUAGE = 'language'
_LANGUAGE_KEY_FILE_NAMING = 'file_naming'
_LANGUAGE_KEY_DISTRIBUTIONS = 'distributions'
_LANGUAGE_KEY_PROPERTY_NAMING = 'property_naming'
_LANGUAGE_KEY_TYPE_NAMING = 'type_naming'
_LANGUAGE_KEY_INDENT = 'indent'
_LANGUAGE_KEY_TRANSFORM = 'transform'
_LANGUAGE_KEY_TYPE = 'type'
_LANGUAGE_KEY_NAME = 'name'
_LANGUAGE_KEY_AS = 'as'
_LANGUAGE_KEY_DISTRIBUTOR = 'distributor'

# Property keys.
_PROPERTY_KEY_VALUE = 'value'
_PROPERTY_KEY_HIDDEN = 'hidden'
_PROPERTY_KEY_COMMENT = 'comment'

# Distribution types.
_DISTRIBUTION_TYPE_GIT = 'git'


class UnknownPropertyTypeException(Exception):
    def __init__(self, property_type: str):
        super().__init__(f'Unknown property type {property_type}')


class UnknownLanguageException(Exception):
    def __init__(self, language: str):
        super().__init__(f'Unknown language {language}')


class SeveralLanguagePluginsException(Exception):
    def __init__(self, language: str):
        super().__init__(f'Several language plugins found for {language}')


class NoLanguagePluginException(Exception):
    def __init__(self, language_names: List[str]):
        super().__init__(f'No language plugin found for {' or '.join(language_names)}')


class AliasAlreadyInUseException(Exception):
    def __init__(self, alias: str):
        super().__init__(f'The include-alias \'{alias}\' is already in use')


class DistributorNotFoundException(Exception):
    def __init__(self, distributor: str):
        super().__init__(f'The distributor \'{distributor}\' could not be found')


class Config:
    """
    Handles the config evaluation by parsing the provided YAML string via the parse-method.
    """

    @staticmethod
    def read(path: str, distributor_credentials: List[DistributorCredentials]) -> List[LanguageConfigBase]:
        """
        Reads the provided YAML configuration file and generates a list of language configurations.

        :param path: Path to load the YAML file from (see example/test-config.yaml for configuration details).
        :type path:  str

        :return: Language configurations which further can be dumped as config files.
        :rtype:  List[LanguageConfigBase]
        """
        return Config._read(path, distributor_credentials=distributor_credentials)[0]

    @staticmethod
    def parse(content: str, config_name: str, distributor_credentials: List[DistributorCredentials]) \
        -> List[LanguageConfigBase]:
        """
        Parses the provided YAML configuration string and returns the corresponding language configurations.

        :param content:     YAML configuration strings. For config details, please check the test-config.yaml in
                            the example folder.
        :type content:      str
        :param config_name: Output config file name. NOTE: The actual file name format might be overruled by
                            the specified file_naming rule from the config.
        :type config_name:  str

        :return: Language configurations which further can be dumped as config files.
        :rtype:  List[LanguageConfigBase]
        """
        return Config._parse(content, config_name, distributor_credentials=distributor_credentials)[0]

    @staticmethod
    def _read(
        path: str,
        namespace: str='',
        namespaces: List[str]=None,
        distributor_credentials: List[DistributorCredentials]=[],
    ) -> List[LanguageConfigBase]:
        """
        Reads the provided YAML configuration file and generates a list of language configurations.

        :param path:      Path to load the YAML file from (see example/test-config.yaml for configuration details).
        :type path:       str
        :param namespace: Specifies a namespace for the config. If None or empty, no namespace will be set.
        :type nammespace: str

        :return: Language configurations which further can be dumped as config files.
        :rtype:  List[LanguageConfigBase]
        """
        with open(path, 'r') as f:
            content = f.read()

        # Prepare config name.
        last_part = path.replace(r'\\', '/').split('/')[-1]

        if '.' in last_part:
            config_name = '.'.join(last_part.split('.')[0:-1])
        else:
            config_name = last_part
        return Config._parse(
            content,
            config_name,
            namespace,
            os.path.dirname(path),
            namespaces,
            distributor_credentials
        )

    @staticmethod
    def _parse(
        content: str,
        config_name: str,
        namespace: str='',
        directory: str='',
        namespaces: List[str]=None,
        distributor_credentials: List[DistributorCredentials]=[],
    ) -> Tuple[List[LanguageConfigBase], List[Property]]:
        """
        Parses the provided YAML configuration string and returns the corresponding language configurations.

        :param content:     YAML configuration strings. For config details, please check the test-config.yaml in
                            the example folder.
        :type content:      str
        :param config_name: Output config file name. NOTE: The actual file name format might be overruled by
                            the specified file_naming rule from the config.
        :type config_name:  str
        :param namespace:   Specifies a namespace for the config. If None or empty, no namespace will be set.
        :type nammespace:   str

        :raises AliasAlreadyInUseException: Raised if an included config file uses an already defined alias.

        :return: Language configurations which further can be dumped as config files.
        :rtype:  List[LanguageConfigBase]
        """
        plugin_loader = PluginLoader()
        yaml_object = yaml.safe_load(content)
        validated_object = Config._schema().validate(yaml_object)
        language_configs: List[LanguageConfigBase] = []
        properties: List[Property] = []
        language_config_plugins = plugin_loader.get_language_config_plugins()
        distributor_plugins = plugin_loader.get_distributor_plugins()

        # Since a default list cannot be assigned to the namespaces variable in the method header, because it only
        # gets initialized once and then the list gets re-used (see https://stackoverflow.com/a/1145781), make sure
        # that namespaces gets set to a freshly created list if it hasn't already been until now.
        if not namespaces:
            namespaces = []

        # Evaluate included files and their properties.
        if _KEY_INCLUDES in validated_object:
            for inclusion in validated_object[_KEY_INCLUDES]:
                ignore = inclusion[_KEY_IGNORE] if _KEY_IGNORE in inclusion else False

                # If inclusion shall not be ignored, include it.
                if not ignore:
                    inclusion_namespace = inclusion[_INCLUDE_KEY_AS]

                    # Make sure that a included config file does not re-define an alias.
                    if inclusion_namespace in namespaces:
                        raise AliasAlreadyInUseException(inclusion_namespace)
                    else:
                        namespaces.append(inclusion_namespace)
                    inclusion_path = inclusion[_INCLUDE_KEY_PATH]

                    # If the provided path is relative, incorporate the provided directory into the path.
                    if not os.path.isabs(inclusion_path):
                        inclusion_path = os.path.join(directory, inclusion_path)

                    # Read included config and put properties into property list.
                    for inclusion_property in Config._read(inclusion_path, inclusion_namespace, namespaces)[1]:
                        inclusion_property.hidden = True  # Included properties are not being exported by default.
                        properties.append(inclusion_property)

        # Collect properties as they are the same for all languages.
        for property in validated_object[_KEY_PROPERTIES]:
            ignore = property[_KEY_IGNORE] if _KEY_IGNORE in property else False

            # If property shall not be ignored, include it.
            if not ignore:
                properties.append(Property(
                    name=property[_LANGUAGE_KEY_NAME],
                    value=property[_PROPERTY_KEY_VALUE],
                    property_type=property[_LANGUAGE_KEY_TYPE],
                    hidden=property[_PROPERTY_KEY_HIDDEN] if _PROPERTY_KEY_HIDDEN in property else None,
                    comment=property[_PROPERTY_KEY_COMMENT] if _PROPERTY_KEY_COMMENT in property else None,
                    namespace=namespace,
                ))

        # Evaluate each language setting one by one.
        if _KEY_LANGUAGES in validated_object:
            for language in validated_object[_KEY_LANGUAGES]:
                ignore = language[_KEY_IGNORE] if _KEY_IGNORE in language else False

                # If language shall not be ignored, include it.
                if not ignore:
                    naming_conventions = LanguageConfigNamingConventions()
                    language_name = language[_LANGUAGE_KEY_LANGUAGE]
                    indent = language[_LANGUAGE_KEY_INDENT] if _LANGUAGE_KEY_INDENT in language else None
                    transform = language[_LANGUAGE_KEY_TRANSFORM] if _LANGUAGE_KEY_TRANSFORM in language else None

                    # Evaluate language.

                    # Evaluate file naming-convention.
                    naming_conventions.file_naming_convention = Config._evaluate_naming_convention_type(
                        language[_LANGUAGE_KEY_FILE_NAMING] if _LANGUAGE_KEY_FILE_NAMING in language else None
                    )

                    # Evaluate properties naming-convention.
                    naming_conventions.properties_naming_convention = Config._evaluate_naming_convention_type(
                        language[_LANGUAGE_KEY_PROPERTY_NAMING] if _LANGUAGE_KEY_PROPERTY_NAMING in language else None
                    )

                    # Evaluate type naming-convention.
                    naming_conventions.type_naming_convention = Config._evaluate_naming_convention_type(
                        language[_LANGUAGE_KEY_TYPE_NAMING] if _LANGUAGE_KEY_TYPE_NAMING in language else None
                    )
                    config_type = Config._evaluate_language_config(language_config_plugins, language_name)

                    language_configs.append(config_type(
                        config_name=config_name,
                        properties=properties,
                        indent=indent,
                        transform=transform,
                        naming_conventions=naming_conventions,
                        distributors=Config._evaluate_distributors(
                            language, distributor_plugins, distributor_credentials
                        ),

                        # Pass all language props as additional_props to let the specific
                        # generator decide which props it requires additionally.
                        additional_props=language,
                    ))

        return language_configs, properties
    
    @staticmethod
    def _schema() -> Schema:
        """
        Returns the config validation schema.

        :return: Config validation schema.
        :rtype:  Schema
        """
        return Schema({
            Optional(_KEY_INCLUDES): [{
                _INCLUDE_KEY_PATH: str,
                _INCLUDE_KEY_AS: str,
                Optional(_KEY_IGNORE): bool,
            }],
            Optional(_KEY_LANGUAGES): [{
                _LANGUAGE_KEY_LANGUAGE: str,
                Optional(_LANGUAGE_KEY_FILE_NAMING): str,
                Optional(_LANGUAGE_KEY_INDENT): int,
                Optional(_LANGUAGE_KEY_DISTRIBUTIONS): [{
                    _LANGUAGE_KEY_DISTRIBUTOR: str,
                    Optional(_LANGUAGE_KEY_AS): str,
                    Optional(object): object,  # Collect other properties.
                    Optional(_KEY_IGNORE): bool,
                }],
                Optional(_KEY_IGNORE): bool,
                Optional(object): object  # Collect other properties.
            }],
            _KEY_PROPERTIES: [{
                _LANGUAGE_KEY_TYPE: Use(Config._evaluate_data_type),
                _LANGUAGE_KEY_NAME: str,
                _PROPERTY_KEY_VALUE: Or(str, bool, int, float),
                Optional(_PROPERTY_KEY_HIDDEN): bool,
                Optional(_PROPERTY_KEY_COMMENT): str,
                Optional(_KEY_IGNORE): bool,
            }]
        })
    
    @staticmethod
    def _evaluate_language_config(language_plugins: List[Plugin], language_name: str) -> Type[LanguageConfigBase]:
        """
        Evaluates the corresponding language config from a language plugin list for the given language name.

        :param language_plugins: List of language plugins to search in.
        :type language_plugins:  List[Plugin]
        :param language_name:    Language name to look for.
        :type language_name:     str

        :raises SeveralLanguagePluginsException: Raised if several plugins were found for the requested language.
        :raises UnknownLanguageException:        Raised if an unsupported language was used in the config.

        :return: The corresponding language config class.
        :rtype:  Type[LanguageConfigBase]
        """
        NINJA_BEAR_LANGUAGE_PREFIX = 'ninja-bear-language-'
        language_config_type = None

        # Make sure only language configs get processed.
        language_plugins = [p for p in language_plugins if p.get_type() == PluginType.LANGUAGE_CONFIG]

        # Remove ninja-bear prefix.
        language_name_cleaned = re.sub(rf'^{NINJA_BEAR_LANGUAGE_PREFIX}', '', language_name)

        # Create possible language names.
        language_names = [f'{NINJA_BEAR_LANGUAGE_PREFIX}{language_name_cleaned}', language_name_cleaned]

        for plugin in language_plugins:
            if plugin.get_name() in language_names:
                if not language_config_type:
                    language_config_type = plugin.get_class_type()
                else:
                    raise SeveralLanguagePluginsException(language_name)

        if not language_config_type:
            raise UnknownLanguageException(language_names)
        return language_config_type

    
    @staticmethod
    def _evaluate_data_type(type: str) -> PropertyType:
        """
        Evaluates a properties data type.

        :param type: Property type string (e.g., bool | string | ...).
        :type type:  str

        :raises UnknownPropertyTypeException: Raised if an unsupported property type was used in the config.

        :return: The corresponding PropertyType enum value.
        :rtype:  PropertyType
        """
        try:
            type = PropertyType(type)
        except ValueError:
            raise UnknownPropertyTypeException(type)
        return type
    
    @staticmethod
    def _evaluate_distributors(
        language_config: Dict[str, any],
        distributor_plugins: List[Plugin]=[],
        distributor_credentials: List[DistributorCredentials]=[]
    ) -> List[DistributorBase]:
        """
        Evaluates specified distributors of a language.

        :param language_config:         Language config object.
        :type language_config:          Dict[str, any]
        :param distributor_credentials: Potentially required credentials, defaults to []
        :type distributor_credentials:  List[DistributorCredential], optional

        :return: List of evaluated distributors for the given language.
        :rtype:  List[DistributorBase]
        """

        distributors = []
        credentials_map = {}

        # Map credential list to dictionary based on the credential alias for easer access.
        for distributor_credential in distributor_credentials:
            credentials_map[distributor_credential.distribution_alias] = distributor_credential

        # Get distributions config if provided.
        distributor_configs = language_config[_LANGUAGE_KEY_DISTRIBUTIONS] \
            if _LANGUAGE_KEY_DISTRIBUTIONS in language_config \
            else None
        
        # Check if distributions are provided.
        if distributor_configs:

            # Make sure distributor_configs is a list.
            if not isinstance(distributor_configs, list):
                distributor_configs = [distributor_configs]

            for distributor_config in distributor_configs:
                ignore = distributor_config[_KEY_IGNORE] if _KEY_IGNORE in distributor_config else False

                # If distributor shall not be ignored, include it.
                if not ignore:
                    def from_config(key: str):
                        return distributor_config[key] if key in distributor_config else None

                    used_distributor = from_config(_LANGUAGE_KEY_DISTRIBUTOR)
                    found_distributors_classes = [plugin.get_class_type() for plugin in distributor_plugins if
                        plugin.get_type() == PluginType.DISTRIBUTOR and plugin.get_name() == used_distributor
                    ]
                    alias = from_config(_LANGUAGE_KEY_AS)

                    if len(found_distributors_classes):
                        found_distributor_class = found_distributors_classes[0]
                        distributors.append(found_distributor_class(
                            distributor_config,
                            credentials_map[alias] if alias in credentials_map else None
                        ))
                    else:
                        raise DistributorNotFoundException(used_distributor)

        return distributors
    
    @staticmethod
    def _evaluate_naming_convention_type(naming_convention: str) -> NamingConventionType:
        """
        Evaluates which naming convention type to use for the output file.

        :param naming_convention: Naming convention string (e.g., snake | camel | ...).
        :type naming_convention:  str

        :return: The corresponding NamingConventionType enum value.
        :rtype:  NamingConventionType
        """
        if naming_convention == 'snake':
            naming_convention = NamingConventionType.SNAKE_CASE
        elif naming_convention == 'screaming_snake':
            naming_convention = NamingConventionType.SCREAMING_SNAKE_CASE
        elif naming_convention == 'camel':
            naming_convention = NamingConventionType.CAMEL_CASE
        elif naming_convention == 'pascal':
            naming_convention = NamingConventionType.PASCAL_CASE
        elif naming_convention == 'kebap':
            naming_convention = NamingConventionType.KEBAP_CASE
        return naming_convention
