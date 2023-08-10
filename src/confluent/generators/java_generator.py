from ..base.generator_base import GeneratorBase
from ..base.property import Property
from ..base.property_type import PropertyType


class JavaGenerator(GeneratorBase):
    """
    Java specific generator. For more information about the generator methods, refer to GeneratorBase.
    """
    _ATTRIBUTE_PACKAGE = 'package'

    def _property_before_class(self, _: Property) -> str:
        return ''

    def _property_in_class(self, property: Property) -> str:
        match property.type:
            case PropertyType.BOOL:
                type = 'boolean'
                value = 'true' if property.value else 'false'
            case PropertyType.INT:
                type = 'int'
                value = property.value
            case PropertyType.FLOAT:
                type = 'float'
                value = f'{property.value}f'
            case PropertyType.DOUBLE:
                type = 'double'
                value = f'{property.value}d'
            case PropertyType.STRING | PropertyType.REGEX:
                type = 'String'
                value = property.value.replace('\\', '\\\\')  # TODO: Might need to be refined.
                value = f'"{value}"'  # Wrap in quotes.
            case _:
                raise Exception('Unknown type')

        return f'public final static {type} {property.name} = {value};'

    def _property_comment(self, comment: str) -> str:
        return f' /* {comment} */'
    
    def _before_class(self, **props) -> str:
        if self._ATTRIBUTE_PACKAGE not in props:
            raise Exception('Java requires a package definition')
        else:
            package = props[self._ATTRIBUTE_PACKAGE]
        
        if not package:
            raise Exception('No package name provided')
        return f'package {package};\n\n'

    def _after_class(self, **props) -> str:
        return ''

    def _start_class(self, class_name: str) -> str:
        return f'public class {class_name} {{'

    def _end_class(self) -> str:
        return '}'
