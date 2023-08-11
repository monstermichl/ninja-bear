from ..base.name_converter import NamingConventionType
from ..base.generator_base import GeneratorBase
from ..base.property import Property
from ..base.property_type import PropertyType


class NewLanguageGenerator(GeneratorBase):
    """
    NewLanguage specific generator. For more information about the generator methods, refer to GeneratorBase.
    """

    def _default_type_naming_convention(self) -> NamingConventionType:
        pass  # TODO: Implement according to the new language.

    def _property_before_type(self, property: Property) -> str:
        pass  # TODO: Implement according to the new language.

    def _property_in_type(self, property: Property) -> str:
        pass  # TODO: Implement according to the new language.

    def _property_comment(self, comment: str) -> str:
        pass  # TODO: Implement according to the new language.
    
    def _before_type(self) -> str:
        pass  # TODO: Implement according to the new language.

    def _after_type(self) -> str:
        pass  # TODO: Implement according to the new language.

    def _start_type(self, type_name: str) -> str:
        pass  # TODO: Implement according to the new language.

    def _end_type(self) -> str:
        pass  # TODO: Implement according to the new language.
