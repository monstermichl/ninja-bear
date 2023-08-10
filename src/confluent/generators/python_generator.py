from ..base.generator_base import GeneratorBase
from ..base.property import Property
from ..base.property_type import PropertyType


class PythonGenerator(GeneratorBase):
    """
    Python specific generator. For more information about the generator methods, refer to GeneratorBase.
    """

    def _create_property(self, property: Property) -> str:
        match property.type:
            case PropertyType.BOOL:
                value = 'True' if property.value else 'False'
            case PropertyType.INT | PropertyType.FLOAT | PropertyType.DOUBLE:
                value = property.value
            case PropertyType.STRING:
                value = property.value.replace('\\', '\\\\')  # TODO: Might need to be refined.
                value = f'\'{value}\''  # Wrap in single quotes.
            case PropertyType.REGEX:
                value = f'r\'{property.value}\''  # Wrap in single quotes.
            case _:
                raise Exception('Unknown type')

        return f'{property.name} = {value}'
    
    def _create_comment(self, comment: str) -> str:
        return f'  # {comment}'
    
    def _before_class(self, **props) -> str:
        newlines = 3 * '\n'
        return f'from enum import Enum{newlines}'

    def _after_class(self, **props) -> str:
        return ''

    def _start_class(self) -> str:
        return f'class {self._class_name}(Enum):'

    def _end_class(self) -> str:
        return ''
