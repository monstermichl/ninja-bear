from .name_converter import NamingConventionType
from .generator_naming_conventions import GeneratorNamingConventions


class LanguageConfigNamingConventions(GeneratorNamingConventions):
    file_naming_convention: NamingConventionType = None
