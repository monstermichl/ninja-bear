from __future__ import annotations
import os
import re
from typing import Dict, List, Tuple, Type

import yaml
from schema import Schema, Use, Optional, Or

from .plugin_manager import Plugin, PluginManager, PluginType
from .name_converter import NamingConventionType
from .property import Property
from .property_type import PropertyType
from .language_config_base import LanguageConfigBase
from .language_config_naming_conventions import LanguageConfigNamingConventions
from .distributor_base import DistributorBase
from .distributor_credentials import DistributorCredentials
from .meta_data_settings import MetaDataSettings

# Main keys.
_KEY_INCLUDES = 'includes'
_KEY_TRANSFORMERS = 'transformers'
_KEY_DISTRIBUTORS = 'distributors'
_KEY_LANGUAGES = 'languages'
_KEY_PROPERTIES = 'properties'
_KEY_META = 'meta'

# Common keys.
_KEY_AS = 'as'
_KEY_IGNORE = 'ignore'

# Include keys.
_INCLUDE_KEY_PATH = 'path'

# Transformer keys.
_TRANSFORMER_KEY_TRANSFORMER = 'transformer'

# Distributor keys.
_DISTRIBUTOR_KEY_DISTRIBUTOR = 'distributor'

# Language keys.
_LANGUAGE_KEY_LANGUAGE = 'language'
_LANGUAGE_KEY_FILE_NAMING = 'file_naming'
_LANGUAGE_KEY_PROPERTY_NAMING = 'property_naming'
_LANGUAGE_KEY_TYPE_NAMING = 'type_naming'
_LANGUAGE_KEY_INDENT = 'indent'
_LANGUAGE_KEY_TRANSFORMERS = _KEY_TRANSFORMERS
_LANGUAGE_KEY_DISTRIBUTORS = _KEY_DISTRIBUTORS

_LANGUAGE_KEY_TYPE = 'type'
_LANGUAGE_KEY_NAME = 'name'

# Property keys.
_PROPERTY_KEY_VALUE = 'value'
_PROPERTY_KEY_HIDDEN = 'hidden'
_PROPERTY_KEY_COMMENT = 'comment'

# Meta keys.
_META_KEY_USER = 'user'
_META_KEY_DATE = 'date'
_META_KEY_TIME = 'time'
_META_KEY_VERSION = 'version'
_META_KEY_LINK = 'link'


class UnknownPropertyTypeException(Exception):
    def __init__(self, property_type: str):
        super().__init__(f'Unknown property type {property_type}')


class SeveralPluginsException(Exception):
    def __init__(self, type: str, name: str):
        super().__init__(f'Several {type} plugins found for {name}')


class SeveralLanguagePluginsException(SeveralPluginsException):
    def __init__(self, language: str):
        super().__init__('language', language)


class NoLanguagePluginException(Exception):
    def __init__(self, language_names: List[str]):
        super().__init__(f'No language plugin found for {" or ".join(language_names)}')


class AliasAlreadyInUseException(Exception):
    def __init__(self, alias: str):
        super().__init__(f'The include-alias \'{alias}\' is already in use')


class SeveralDistributorPluginsException(SeveralPluginsException):
    def __init__(self, distributor: str):
        super().__init__('distributor', distributor)


class DistributorNotFoundException(Exception):
    def __init__(self, distributor: str):
        super().__init__(f'The distributor \'{distributor}\' could not be found')


class DefinitionAliasNotFoundException(Exception):
    def __init__(self, type: str, alias: str):
        super().__init__(f'The {type} alias \'{alias}\' could not be found')


class TransformerAliasNotFoundException(DefinitionAliasNotFoundException):
    def __init__(self, alias: str):
        super().__init__('transformer', alias)


class DistributorAliasNotFoundException(DefinitionAliasNotFoundException):
    def __init__(self, alias: str):
        super().__init__('distributor', alias)


class Config:
    """
    Handles the config evaluation by parsing the provided YAML string via the parse-method.
    """

    @staticmethod
    def read(
        path: str,
        distributor_credentials: List[DistributorCredentials]=None,
        plugins: List[Plugin]=None,
    ) -> List[LanguageConfigBase]:
        """
        Reads the provided YAML configuration file and generates a list of language configurations.

        :param path: Path to load the YAML file from (see example/test-config.yaml for configuration details).
        :type path:  str
        TODO: Update parameter documentation!!!

        :return: Language configurations which further can be dumped as config files.
        :rtype:  List[LanguageConfigBase]
        """
        return Config._read(
            path,
            distributor_credentials=distributor_credentials,
            plugins=plugins
        )[0]

    @staticmethod
    def parse(
        content: str,
        config_name: str,
        distributor_credentials: List[DistributorCredentials]=None,
        plugins: List[Plugin]=None,
    ) -> List[LanguageConfigBase]:
        """
        Parses the provided YAML configuration string and returns the corresponding language configurations.

        :param content:     YAML configuration strings. For config details, please check the test-config.yaml in
                            the example folder.
        :type content:      str
        :param config_name: Output config file name. NOTE: The actual file name format might be overruled by
                            the specified file_naming rule from the config.
        :type config_name:  str
        TODO: Update parameter documentation!!!

        :return: Language configurations which further can be dumped as config files.
        :rtype:  List[LanguageConfigBase]
        """
        return Config._parse(
            content,
            config_name,
            distributor_credentials=distributor_credentials,
            plugins=plugins
        )[0]

    @staticmethod
    def _read(
        path: str,
        namespace: str='',
        namespaces: List[str]=None,
        distributor_credentials: List[DistributorCredentials]=None,
        plugins: List[Plugin]=None,
    ) -> List[LanguageConfigBase]:
        """
        Reads the provided YAML configuration file and generates a list of language configurations.

        :param path:      Path to load the YAML file from (see example/test-config.yaml for configuration details).
        :type path:       str
        :param namespace: Specifies a namespace for the config. If None or empty, no namespace will be set.
        :type nammespace: str
        TODO: Update parameter documentation!!!

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
            distributor_credentials,
            plugins,
        )

    @staticmethod
    def _parse(
        content: str,
        config_name: str,
        namespace: str='',
        directory: str='',
        namespaces: List[str]=None,
        distributor_credentials: List[DistributorCredentials]=None,
        plugins: List[Plugin]=None,
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
        TODO: Update parameter documentation!!!

        :raises AliasAlreadyInUseException: Raised if an included config file uses an already defined alias.

        :return: Language configurations which further can be dumped as config files.
        :rtype:  List[LanguageConfigBase]
        """
        plugin_manager = PluginManager(plugins)
        yaml_object = yaml.safe_load(content)
        validated_object = Config._schema().validate(yaml_object)
        language_configs: List[LanguageConfigBase] = []
        properties: List[Property] = []
        language_config_plugins = plugin_manager.get_language_config_plugins()
        transformers = Config._evaluate_transformers(validated_object)
        distributor_plugins = plugin_manager.get_distributor_plugins()
        distributors = Config._evaluate_distributors(validated_object, distributor_plugins, distributor_credentials)
        meta_data_settings = Config._evaluate_meta_data_settings(validated_object)

        # Since a default list cannot be assigned to parameters in the method header, because it only gets initialized
        # once and then the list gets re-used (see https://stackoverflow.com/a/1145781), make sure to set undefined
        # variables to list (see also https://docs.python.org/3/reference/compound_stmts.html#function-definitions).
        if not namespaces:
            namespaces = []
        if not distributor_credentials:
            distributor_credentials = []
        if not plugins:
            plugins = []

        # Evaluate included files and their properties.
        if _KEY_INCLUDES in validated_object:
            for inclusion in validated_object[_KEY_INCLUDES]:
                ignore = inclusion[_KEY_IGNORE] if _KEY_IGNORE in inclusion else False

                # If inclusion shall not be ignored, include it.
                if not ignore:
                    inclusion_namespace = inclusion[_KEY_AS]

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
                        transformers=Config._evaluate_language_transformers(language, transformers),
                        naming_conventions=naming_conventions,
                        distributors=Config._evaluate_language_distributors(language, distributors),
                        meta_data_settings=meta_data_settings,

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
                _KEY_AS: str,
                Optional(_KEY_IGNORE): bool,
            }],
            Optional(_KEY_TRANSFORMERS): [{
                _TRANSFORMER_KEY_TRANSFORMER: str,
                _KEY_AS: str,
                Optional(_KEY_IGNORE): bool,
            }],
            Optional(_KEY_DISTRIBUTORS): [{
                _DISTRIBUTOR_KEY_DISTRIBUTOR: str,
                _KEY_AS: str,
                Optional(_KEY_IGNORE): bool,
            }],
            Optional(_KEY_LANGUAGES): [{
                _LANGUAGE_KEY_LANGUAGE: str,
                Optional(_LANGUAGE_KEY_FILE_NAMING): str,
                Optional(_LANGUAGE_KEY_INDENT): int,
                Optional(_LANGUAGE_KEY_TRANSFORMERS): [str],
                Optional(_LANGUAGE_KEY_DISTRIBUTORS): [str],
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
            }],
            Optional(_KEY_META): {
                Optional(_META_KEY_USER): bool,
                Optional(_META_KEY_DATE): bool,
                Optional(_META_KEY_TIME): bool,
                Optional(_META_KEY_VERSION): bool,
                Optional(_META_KEY_LINK): bool,
            },
        })

    @staticmethod
    def _plugin_names(prefix: str, plugin_name: str) -> List[str]:
        NINJA_BEAR_PLUGIN_PREFIX = 'ninja-bear-'

        cleaned_prefix = re.sub(rf'^{NINJA_BEAR_PLUGIN_PREFIX}', '', prefix).strip('-')
        prefix = f'{NINJA_BEAR_PLUGIN_PREFIX}{cleaned_prefix}-'

        # Remove ninja-bear prefix.
        plugin_name_cleaned = re.sub(rf'^{prefix}', '', plugin_name)

        # Add prefix.
        prefixed_plugin_name_cleaned = f'{prefix}{plugin_name_cleaned}'

        def replace_dashes(s: str):
            return s.replace('-', '_')

        # Create possible plugin names.
        return list(set([
            plugin_name_cleaned,
            prefixed_plugin_name_cleaned,
            replace_dashes(plugin_name_cleaned),
            replace_dashes(prefixed_plugin_name_cleaned),
        ]))
    
    @staticmethod
    def _evaluate_meta_data_settings(validated_object: object) -> MetaDataSettings:
        """
        Evaluates the specified meta data settings.

        :param validated_object: Schema validated config object.
        :type validated_object:  object

        :return: Dictionary of defined transformer-scripts where the key is the alias.
        :rtype:  MetaDataSettings
        """
        meta_data_settings = MetaDataSettings()

        if _KEY_META in validated_object:
            settings = validated_object[_KEY_META]

            def from_settings(key: str) -> bool:
                return settings[key] if key in settings else None

            meta_data_settings.user = from_settings(_META_KEY_USER)
            meta_data_settings.date = from_settings(_META_KEY_DATE)
            meta_data_settings.time = from_settings(_META_KEY_TIME)
            meta_data_settings.version = from_settings(_META_KEY_VERSION)
            meta_data_settings.link = from_settings(_META_KEY_LINK)

        return meta_data_settings

    @staticmethod
    def _evaluate_language_config(language_plugins: List[Plugin], language_name: str) -> Type[LanguageConfigBase]:
        """
        Evaluates the corresponding language config from a language plugin list for the given language name.

        :param language_plugins: List of language plugins to search in.
        :type language_plugins:  List[Plugin]
        :param language_name:    Language name to look for.
        :type language_name:     str

        :raises SeveralLanguagePluginsException: Raised if several plugins were found for the requested language.
        :raises NoLanguagePluginException:       Raised if an unsupported language was used in the config.

        :return: The corresponding language config class.
        :rtype:  Type[LanguageConfigBase]
        """
        language_config_type = None

        # Make sure only language configs get processed.
        language_plugins = [p for p in language_plugins if p.get_type() == PluginType.LANGUAGE_CONFIG]

        # Create possible language names.
        language_names = Config._plugin_names('language', language_name)

        for plugin in language_plugins:
            if plugin.get_name() in language_names:
                if not language_config_type:
                    language_config_type = plugin.get_class_type()
                else:
                    raise SeveralLanguagePluginsException(language_name)

        if not language_config_type:
            raise NoLanguagePluginException(language_names)
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
    def _evaluate_transformers(validated_object: object) -> Dict[str, DistributorBase]:
        """
        Evaluates specified transformers.

        :param validated_object: Schema validated config object.
        :type validated_object:  object

        :return: Dictionary of defined transformer-scripts where the key is the alias.
        :rtype:  Dict[str, str]
        """
        transformers = {}

        if _KEY_TRANSFORMERS in validated_object:
            transformer_configs = validated_object[_KEY_TRANSFORMERS]

            for transformer_config in transformer_configs:
                ignore = transformer_config[_KEY_IGNORE] if _KEY_IGNORE in transformer_config else False

                # If distributor shall not be ignored, include it.
                if not ignore:
                    def from_config(key: str):
                        return transformer_config[key] if key in transformer_config else None

                    transformer_script = from_config(_TRANSFORMER_KEY_TRANSFORMER)
                    alias = from_config(_KEY_AS)

                    transformers[alias] = transformer_script

        return transformers
    
    @staticmethod
    def _evaluate_language_referenced_definitions(
        language_config: Dict[str, any],
        definitions: Dict[str, any],
        key: str,
        exception_type: Type[DefinitionAliasNotFoundException],
    ) -> List[any]:
        """
        Evaluates specified transformers of a language.

        :param language_config: Language config object.
        :type language_config:  Dict[str, any]
        :param definitions:     Dictionary of defined definitions (e.g. distributors) where the key is the alias.
        :type definitions:      Dict[str, any]
        :param key:             Key to look for in the language config.
        :type key:              str
        :param exception_type:  Exception type to instantiate if an alias could not be found.
        :type exception_type:   Type[DefinitionAliasNotFoundException]

        :return: List of evaluated definitions (e.g. distributors) for the given language.
        :rtype:  List[any]
        """
        language_definitions = []

        # This time better safe than sorry.
        if not language_config:
            language_config = {}
        if not definitions:
            definitions = {}

        # Get definition references if provided.
        definition_aliases = language_config[key] if key in language_config else []
        
        # Collect all definitions that belong to the language.
        for language_alias in definition_aliases:
            if language_alias not in definitions:
                raise exception_type(language_alias)
            language_definitions.append(definitions[language_alias])

        return language_definitions
    
    @staticmethod
    def _evaluate_language_transformers(
        language_config: Dict[str, any],
        transformers: Dict[str, str]
    ) -> List[str]:
        """
        Evaluates specified transformers of a language.

        :param language_config: Language config object.
        :type language_config:  Dict[str, any]
        :param distributors:    Dictionary of defined transformer scripts where the key is the alias.
        :type distributors:     Dict[str, str], optional

        :return: List of evaluated transformer scripts for the given language.
        :rtype:  List[str]
        """
        return Config._evaluate_language_referenced_definitions(
            language_config,
            transformers,
            _LANGUAGE_KEY_TRANSFORMERS,
            TransformerAliasNotFoundException,
        )
    
    @staticmethod
    def _evaluate_distributors(
        validated_object: object,
        distributor_plugins: List[Plugin]=None,
        distributor_credentials: List[DistributorCredentials]=None
    ) -> Dict[str, DistributorBase]:
        """
        Evaluates specified distributors.

        :param validated_object:        Schema validated config object.
        :type validated_object:         object
        :param distributor_plugins:     List of all discovered distributor plugins, defaults to None
        :type distributor_plugins:      List[Plugin], optional
        :param distributor_credentials: Potentially required credentials, defaults to None
        :type distributor_credentials:  List[DistributorCredential], optional

        :return: Dictionary of defined distributors where the key is the alias.
        :rtype:  Dict[str, DistributorBase]
        """
        distributors = {}

        if _KEY_DISTRIBUTORS in validated_object:
            distributor_configs = validated_object[_KEY_DISTRIBUTORS]
            credentials_map = {}

            # Since a default list cannot be assigned to parameters in the method header, because it only gets
            # initialized once and then the list gets re-used (see https://stackoverflow.com/a/1145781), make
            # sure to set undefined variables to list (see also
            # https://docs.python.org/3/reference/compound_stmts.html#function-definitions).
            if not distributor_plugins:
                distributor_plugins = []
            if not distributor_credentials:
                distributor_credentials = []

            # Make sure only language configs get processed.
            distributor_plugins = [p for p in distributor_plugins if p.get_type() == PluginType.DISTRIBUTOR]

            # Map credential list to dictionary based on the credential alias for easer access.
            for distributor_credential in distributor_credentials:
                credentials_map[distributor_credential.distributor_alias] = distributor_credential

            for distributor_config in distributor_configs:
                ignore = distributor_config[_KEY_IGNORE] if _KEY_IGNORE in distributor_config else False

                # If distributor shall not be ignored, include it.
                if not ignore:
                    def from_config(key: str):
                        return distributor_config[key] if key in distributor_config else None

                    distributor_name = from_config(_DISTRIBUTOR_KEY_DISTRIBUTOR)

                    # Create possible distributor names.
                    distributor_names = Config._plugin_names('distributor', distributor_name)

                    found_distributors_classes = [
                        plugin.get_class_type() for plugin in distributor_plugins if
                        plugin.get_name() in distributor_names
                    ]
                    alias = from_config(_KEY_AS)
                    length = len(found_distributors_classes)

                    if length == 1:
                        found_distributor_class = found_distributors_classes[0]
                        distributors[alias] = found_distributor_class(
                            distributor_config,
                            credentials_map[alias] if alias in credentials_map else None
                        )
                    elif length > 1:
                        raise SeveralDistributorPluginsException(distributor_name)
                    else:
                        raise DistributorNotFoundException(distributor_name)

        return distributors
    
    @staticmethod
    def _evaluate_language_distributors(
        language_config: Dict[str, any],
        distributors: Dict[str, DistributorBase]
    ) -> List[DistributorBase]:
        """
        Evaluates specified distributors of a language.

        :param language_config: Language config object.
        :type language_config:  Dict[str, any]
        :param distributors:    Dictionary of defined distributors where the key is the alias.
        :type distributors:     Dict[str, DistributorBase], optional

        :return: List of evaluated distributors for the given language.
        :rtype:  List[DistributorBase]
        """
        return Config._evaluate_language_referenced_definitions(
            language_config,
            distributors,
            _LANGUAGE_KEY_DISTRIBUTORS,
            DistributorAliasNotFoundException,
        )

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
