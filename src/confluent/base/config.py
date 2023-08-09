from __future__ import annotations
import re
from typing import List

import yaml
from schema import Schema, Use, Optional, Or

from .config_language_mapping import ConfigLanguageMapping
from .name_converter import NamingConventionType
from .property import Property
from .property_type import PropertyType
from .language_type import LanguageType
from .language_config import LanguageConfig


_KEY_LANGUAGES = 'languages'
_KEY_PROPERTIES = 'properties'
_KEY_FILE_NAMING = 'file_naming'
_KEY_INDENT = 'indent'
_KEY_TYPE = 'type'
_KEY_NAME = 'name'
_KEY_VALUE = 'value'
_KEY_HIDDEN = 'hidden'
_KEY_COMMENT = 'comment'

_LANGUAGE_MAPPINGS = ConfigLanguageMapping.get_mappings()


class UnknownSubstitutionException(Exception):
    def __init__(self, substitution_property: str):
        super().__init__(f'Unknown substitution property {substitution_property}')


class RecursiveSubstitutionException(Exception):
    def __init__(self, substitution_property: str):
        super().__init__(f'It\'s not allowed for a property to reference itself ({substitution_property})')


class UnknownPropertyTypeException(Exception):
    def __init__(self, property_type: str):
        super().__init__(f'Unknown property type {property_type}')


class UnknownLanguageException(Exception):
    def __init__(self, language: str):
        super().__init__(f'Unknown language {language}')


class SeveralLanguagesException(Exception):
    def __init__(self, language: str):
        super().__init__(f'Several languages matched for {language}')


class NoLanguageConfigException(Exception):
    def __init__(self, language_type: LanguageType):
        super().__init__(f'No language config found for {language_type}')


class SeveralLanguageConfigsException(Exception):
    def __init__(self, language_type: LanguageType):
        super().__init__(f'Several languages configs found for {language_type}')


class Config:
    """
    Handles the config evaluation by parsing the provided YAML string via the parse-method.

    :raises UnknownSubstitutionException:    Raised if the requested substitution property does not exist.
    :raises RecursiveSubstitutionException:  Raised if a property referenced itself as substitution.
    :raises UnknownPropertyTypeException:    Raised if an unsupported property type was used in the config.
    :raises UnknownLanguageException:        Raised if an unsupported language was used in the config.
    :raises SeveralLanguagesException:       Raised if several mappings were found for the requested language. If this
                                             error arises, it's a package error. Please open an issue at
                                             https://github.com/monstermichl/confluent/issues.
    :raises NoLanguageConfigException:       Raised if no language config mapping was provided for the specified
                                             language type. If this error arises, it's a package error. Please open an
                                             issue at https://github.com/monstermichl/confluent/issues.
    :raises SeveralLanguageConfigsException: Raised if several language config mappings were found for the specified
                                             language type. If this error arises, it's a package error. Please open an
                                             issue at https://github.com/monstermichl/confluent/issues.
    """

    @staticmethod
    def parse(content: str, config_name: str) -> List[LanguageConfig]:
        """
        Parses the provided YAML configuration string and returns the corresponding language configurations.

        :param content:     YAML configuration strings. For config details, please check the test-config.yaml in
                            the example folder.
        :type content:      str
        :param config_name: Output config file name. NOTE: The actual file name format might be overruled by
                            the specified file_naming rule from the config.
        :type config_name:  str

        :raises UnknownSubstitutionException:    Raised if the requested substitution property does not exist.
        :raises RecursiveSubstitutionException:  Raised if a property referenced itself as substitution.

        :return: Language configurations which further can be dumped as config files.
        :rtype:  List[LanguageConfig]
        """
        yaml_object = yaml.safe_load(content)
        validated_object = Config._schema().validate(yaml_object)
        properties: List[Property] = []
        language_configs: List[LanguageConfig] = []

        # Collect properties as they are the same for all languages.
        for property in validated_object[_KEY_PROPERTIES]:
            properties.append(Property(
                property_type = property[_KEY_TYPE],
                name = property[_KEY_NAME],
                value = property[_KEY_VALUE],
                hidden=property[_KEY_HIDDEN] if _KEY_HIDDEN in property else None,
                comment=property[_KEY_COMMENT] if _KEY_COMMENT in property else None,
            ))

        # Substitute property values.
        for property in properties:
            def replace(match):
                substitution_property = match.group(1)
                
                # Substitute property only if it's not the same property as the one
                # which is currently being processed.
                if substitution_property != property.name:
                    found_properties = [
                        search_property.value for search_property in properties if
                        search_property.name == substitution_property
                    ]

                    if not found_properties:
                        raise UnknownSubstitutionException(substitution_property)
                    replacement = found_properties[0]
                else:
                    raise RecursiveSubstitutionException('It\'s not allowed to reference the property itself')
                return replacement
            
            if isinstance(property.value, str):
                property.value = re.sub(r'\${(\w+)}', replace, property.value)

        # Remove hidden properties.
        properties = [property for property in properties if not property.hidden]

        # Evaluate each language setting one by one.
        for language in validated_object[_KEY_LANGUAGES]:
            language_type = language[_KEY_TYPE]
            indent = language[_KEY_INDENT] if _KEY_INDENT in language else None
            file_naming_convention = Config._evaluate_naming_convention_type(
                language[_KEY_FILE_NAMING] if _KEY_FILE_NAMING in language else None
            )
            config_type = Config._evaluate_config_type(language_type)

            language_configs.append(config_type(
                config_name,
                file_naming_convention,
                properties,
                indent,

                # Pass all language props as additional_props to let the specific
                # generator decides which props he requires additionally.
                language,
            ))

        return language_configs
    
    @staticmethod
    def _schema() -> Schema:
        """
        Returns the config validation schema.

        :return: Config validation schema.
        :rtype:  Schema
        """
        return Schema({
            _KEY_LANGUAGES: [{
                _KEY_TYPE: Use(Config._evaluate_language_type),
                Optional(_KEY_FILE_NAMING): str,
                Optional(_KEY_INDENT): int,
                Optional(object): object  # Collect other properties(?).
            }],
            _KEY_PROPERTIES: [{
                _KEY_TYPE: Use(Config._evaluate_data_type),
                _KEY_NAME: str,
                _KEY_VALUE: Or(str, bool, int, float),
                Optional(_KEY_HIDDEN): bool,
                Optional(_KEY_COMMENT): str,
            }]
        })
    
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
        if type == 'bool':
            type = PropertyType.BOOL
        elif type == 'int':
            type = PropertyType.INT
        elif type == 'float':
            type = PropertyType.FLOAT
        elif type == 'double':
            type = PropertyType.DOUBLE
        elif type == 'string':
            type = PropertyType.STRING
        elif type == 'regex':
            type = PropertyType.REGEX
        else:
            raise UnknownPropertyTypeException(type)
        return type

    @staticmethod
    def _evaluate_language_type(language: str) -> LanguageType:
        """
        Evaluates the requested language type.

        :param language: Language to generate a config for (e.g., java | typescript | ...).
        :type language:  str

        :raises UnknownLanguageException:  Raised if an unsupported language was used in the config.
        :raises SeveralLanguagesException: Raised if several mappings were found for the requested language. If this
                                           error arises, it's a package error. Please open an issue at
                                           https://github.com/monstermichl/confluent/issues.

        :return: The corresponding LanguageType enum value.
        :rtype:  LanguageType
        """
        found = [mapping.type for mapping in _LANGUAGE_MAPPINGS if mapping.name == language]
        length = len(found)

        if length == 0:
            raise UnknownLanguageException(language)
        elif length > 1:
            raise SeveralLanguagesException(language)
        return found[0]
    
    @staticmethod
    def _evaluate_config_type(language_type: LanguageType) -> LanguageConfig.__class__:
        """
        Evaluates the languages config type to use for further evaluation.

        :param language_type: Language type to search the corresponding language config for (e.g., LanguageType.JAVA).
        :type language_type:  LanguageType

        :raises NoLanguageConfigException:       Raised if no language config mapping was provided for the specified
                                                 language type. If this error arises, it's a package error. Please open
                                                 an issue at https://github.com/monstermichl/confluent/issues.
        :raises SeveralLanguageConfigsException: Raised if several language config mappings were found for the specified
                                                 language type. If this error arises, it's a package error. Please open
                                                 an issue at https://github.com/monstermichl/confluent/issues.

        :return: The corresponding LanguageConfig derivate type (e.g., JavaConfig.__class__).
        :rtype:  LanguageConfig.__class__
        """
        found = [mapping.config_type for mapping in _LANGUAGE_MAPPINGS if mapping.type == language_type]
        length = len(found)

        if length == 0:
            raise NoLanguageConfigException(language_type)
        elif length > 1:
            raise SeveralLanguageConfigsException('Several language configs found')
        return found[0]
    
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
