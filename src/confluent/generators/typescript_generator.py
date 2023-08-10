from ..base.generator_base import GeneratorBase
from ..base.property import Property
from ..base.property_type import PropertyType


class TypescriptGenerator(GeneratorBase):
    """
    TypeScript specific generator. For more information about the generator methods, refer to GeneratorBase.
    """

    def _property_before_class(self, _: Property) -> str:
        return ''

    def _property_in_class(self, property: Property) -> str:
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

        return f'public static readonly {property.name} = {value};'
    
    def _property_comment(self, comment: str) -> str:
        return f' /* {comment} */'
    
    def _before_class(self, **props) -> str:
        return ''

    def _after_class(self, **props) -> str:
        return ''

    def _start_class(self) -> str:
        return f'export class {self._class_name} {{'

    def _end_class(self) -> str:
        return '}'
