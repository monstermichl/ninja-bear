from abc import ABC, abstractmethod
from typing import List, Self

from .name_converter import NamingConventionType, NameConverter

from .property import Property


class GeneratorBase(ABC):
    _DEFAULT_INDENT = 3

    def __init__(self, class_name: str, properties: List[Property] = [], indent = _DEFAULT_INDENT, additional_props = {}) -> Self:
        self._properties: List[Property] = []
        self._additional_props = additional_props

        self._set_class_name(class_name)
        self.set_indent(indent)

        [self.add_property(property) for property in properties]

    def add_property(self, property: Property) -> Self:
        found_property = len([p for p in self._properties if p.name == property.name]) > 0

        # Make sure that the name doesn't already exist.
        if found_property:
            raise Exception(f'Property name {property.name} already exists')

        self._properties.append(property)

    def set_indent(self, indent: int) -> Self:
        self._indent = indent if indent and indent >= 0 else self._DEFAULT_INDENT

    def dump(self) -> str:
        s = self._before_class(**self._additional_props)
        s += f'{self._start_class()}\n'
        s += '\n'.join([f'{self._create_property_string(property)}' for property in self._properties])
        s += f'\n{self._end_class()}'
        s += self._after_class(**self._additional_props)
        s += '\n'

        return s

    @abstractmethod
    def _create_property(self, property: Property) -> str:
        pass

    @abstractmethod
    def _create_comment(self, comment: str) -> str:
        pass

    @abstractmethod
    def _before_class(self, **props) -> str:
        pass

    @abstractmethod
    def _after_class(self, **props) -> str:
        pass

    @abstractmethod
    def _start_class(self) -> str:
        pass

    @abstractmethod
    def _end_class(self) -> str:
        pass

    def _set_class_name(self, name: str) -> Self:
        if not name:
            raise Exception('No class name provided')

        self._class_name = NameConverter.convert(name, NamingConventionType.PASCAL_CASE)

    def _create_property_string(self, property: Property):
        s = ' ' * self._indent  # Indent space.
        s += self._create_property(property)

        if property.comment:
            s += self._create_comment(property.comment)
        return s
