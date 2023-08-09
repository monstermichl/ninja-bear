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

class Config:

    @staticmethod
    def parse(content: str, config_name: str) -> List[LanguageConfig]:
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
                        raise Exception(f'Unknown substitution property {substitution_property}')
                    replacement = found_properties[0]
                else:
                    raise Exception('It\'s not allowed to reference the property itself')
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
            # Use string as default type.
            type = PropertyType.STRING
        return type

    @staticmethod
    def _evaluate_language_type(language: str) -> LanguageType:
        found = [mapping.type for mapping in _LANGUAGE_MAPPINGS if mapping.name == language]
        length = len(found)

        if length == 0:
            raise Exception('Unknown language')
        elif length > 1:
            raise Exception('Several languages found')
        return found[0]
    
    @staticmethod
    def _evaluate_config_type(language_type: LanguageType) -> LanguageType:
        found = [mapping.config_type for mapping in _LANGUAGE_MAPPINGS if mapping.type == language_type]
        length = len(found)

        if length == 0:
            raise Exception('Unknown language config')
        elif length > 1:
            raise Exception('Several language configs found')
        return found[0]
    
    @staticmethod
    def _evaluate_naming_convention_type(naming_convention: str) -> NamingConventionType:
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
