from ..base.generator_base import GeneratorBase
from ..base.property import Property
from ..base.property_type import PropertyType


class NewLanguageGenerator(GeneratorBase):
    """
    NewLanguage specific generator. For more information about the generator methods, refer to GeneratorBase.
    """

    def _property_before_class(self, property: Property) -> str:
        return ''

    def _property_in_class(self, property: Property) -> str:
        pass  # TODO: Implement according to the new language.

    def _property_comment(self, comment: str) -> str:
        pass  # TODO: Implement according to the new language.
    
    def _before_class(self, **props) -> str:
        pass  # TODO: Implement according to the new language.

    def _after_class(self, **props) -> str:
        pass  # TODO: Implement according to the new language.

    def _start_class(self, class_name: str) -> str:
        pass  # TODO: Implement according to the new language.

    def _end_class(self) -> str:
        pass  # TODO: Implement according to the new language.
