from enum import Enum
from typing import List

from ..base.name_converter import NamingConventionType
from ..base.generator_naming_conventions import GeneratorNamingConventions
from ..base.generator_base import _DEFAULT_INDENT, GeneratorBase
from ..base.property import Property
from ..base.property_type import PropertyType


class ExportType(str, Enum):
    ESM = 'esm'
    COMMON_JS = 'common_js'
    NONE = 'none'


class UnknownExportTypeException(Exception):
    def __init__(self, export_type: str):
        super().__init__(f'Unknown export type {export_type}')



class JavascriptGenerator(GeneratorBase):
    """
    JavaScript specific generator. For more information about the generator methods, refer to GeneratorBase.
    """
    _ATTRIBUTE_EXPORT = 'export'

    def __init__(
        self,
        type_name: str,
        properties: List[Property] = [],
        indent: int = _DEFAULT_INDENT,
        naming_conventions: GeneratorNamingConventions = None,
        additional_props = {}
    ):
        super().__init__(type_name, properties, indent, naming_conventions, additional_props)

        # Evaluate which export type to use.
        self.export_type = self._evaluate_export_type()

    def _default_type_naming_convention(self) -> NamingConventionType:
        return NamingConventionType.PASCAL_CASE

    def _property_before_type(self, _: Property) -> str:
        return ''

    def _property_in_type(self, property: Property) -> str:
        match property.type:
            case PropertyType.BOOL:
                value = 'true' if property.value else 'false'
            case PropertyType.INT | PropertyType.FLOAT | PropertyType.DOUBLE:
                value = property.value
            case PropertyType.STRING:
                value = property.value.replace('\\', '\\\\')  # TODO: Might need to be refined.
                value = f'\'{value}\''  # Wrap in single quotes.
            case PropertyType.REGEX:
                value = f'/{property.value}/'  # Wrap in single quotes.
            case _:
                raise Exception('Unknown type')
            
        return self._create_property(property.name, value)
    
    def _property_after_type(self, _: Property) -> str:
        return ''
    
    def _property_comment(self, comment: str) -> str:
        return f' // {comment}'
    
    def _before_type(self) -> str:
        return ''

    def _after_type(self) -> str:
        # Add module export only if CommonJS is used.
        return f'module.exports = {self._type_name}' if self.export_type == ExportType.COMMON_JS else ''

    def _start_type(self, type_name: str) -> str:
        # Export class only directly if ESM is used.
        export = 'export ' if self.export_type == ExportType.ESM else ''

        return f'{export}class {type_name} {{'

    def _end_type(self) -> str:
        return '}'
    
    def _evaluate_export_type(self) -> ExportType:
        export_type = ExportType.ESM  # Default to ESM.

        if self._ATTRIBUTE_EXPORT in self._additional_props:
            exception_type_string = self._additional_props[self._ATTRIBUTE_EXPORT]

            match exception_type_string:
                case ExportType.ESM:
                    export_type = ExportType.ESM
                case ExportType.COMMON_JS:
                    export_type = ExportType.COMMON_JS
                case ExportType.NONE:
                    export_type = ExportType.NONE
                case _:
                    raise UnknownExportTypeException(exception_type_string)
        return export_type

    def _create_property(self, name: str, value: str):
        # Realize JavaScript constant by defining a Getter.
        return f'static get {name}() {{ return {value}; }}'
