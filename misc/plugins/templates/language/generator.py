from typing import Dict, List
from ninja_bear import GeneratorBase, Property, PropertyType, NamingConventionType, DumpInfo
from ninja_bear.base.generator_configuration import GeneratorConfiguration


class Generator(GeneratorBase):
    """
    <name-upper> specific generator. For more information about the generator methods, refer to GeneratorBase.
    """
    def __init__(self, config: GeneratorConfiguration, properties: List[Property]=None, additional_props: Dict[str, any]=None):
        """
        The constructor usually doesn't have to be overwritten by the implementer. However, if the language requires
        some additional properties (e.g. a package name) they can be retrieved from the additional_props parameter.
        It's also recommended practice to do all additional pre-checks here (e.g. checking if the package name is okay).

        :param config:           Generator configuration.
        :type config:            GeneratorConfiguration
        :param properties:       List of properties to generator by the GeneratorBase derivate, defaults to None
        :type properties:        List[Property], optional
        :param additional_props: All props that might need to be used by the derivating class, defaults to None
        :type additional_props:  Dict[str, any], optional
        """
        super().__init__(config, properties, additional_props)

    def _default_type_naming_convention(self) -> NamingConventionType:
        """
        Specifies the default type naming convention. This is necessary because some languages (e.g. Java)
        require the classes/structs/etc. to have a specific kind of naming format.

        :return: Default naming convention.
        :rtype:  NamingConventionType
        """
        # TODO: Implement
        raise Exception('_default_type_naming_convention method not implemented')
    
    def _line_comment(self, string: str) -> str:
        """
        Turns a string into a line comment.

        :param string: String to turn into a line comment.
        :type string:  str

        :return: Commented string.
        :rtype:  str
        """
        # TODO: Implement
        raise Exception('_line_comment method not implemented')
    
    def _dump(self, info: DumpInfo) -> str:
        """
        This is where the code gets created. TODO: Make sure to also handle indent and comments
        as this is in the implementer's responsibility. For an example implementation, please
        have a look at the ExampleScriptGenerator class in the ninja-bear test.py file.

        :param type_name:  Contains to required information to dump language specific code.
        :type type_name:   DumpInfo

        :return: Dumped type string.
        :rtype:  str
        """
        # TODO: Implement
        raise Exception('_dump method not implemented')
