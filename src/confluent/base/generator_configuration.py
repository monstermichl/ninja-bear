from ..base.generator_naming_conventions import GeneratorNamingConventions

from .configuration_base import ConfigurationBase


class GeneratorConfiguration(ConfigurationBase):
    """
    Encapsulates the configuration properties used by the GeneratorBase class.
    """
    type_name: str
    naming_conventions: GeneratorNamingConventions = None
