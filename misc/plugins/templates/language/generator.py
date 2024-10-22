from ninja_bear import GeneratorBase, Property, PropertyType, NamingConventionType, DumpInfo


class Generator(GeneratorBase):
    """
    <name-upper> specific generator. For more information about the generator methods, refer to GeneratorBase.
    """

    def _default_type_naming_convention(self) -> NamingConventionType:
        """
        Abstract method which must be implemented here to specify the default type naming convention.

        :return: Default naming convention.
        :rtype:  NamingConventionType
        """
        raise Exception('_default_type_naming_convention method not implemented')
    
    def _line_comment(self, string: str) -> str:
        """
        Abstract method which must be implemented here to turn a string into a line comment.

        :param string: String to turn into a line comment.
        :type string:  str

        :return: Commented string.
        :rtype:  str
        """
        raise Exception('_line_comment method not implemented')
    
    def _dump(self, info: DumpInfo) -> str:
        """
        Abstract method which must be implemented here to create a type string.
        This is where the code gets created. TODO: Make sure to also handle
        indent and comments as this is in the implementer's responsibility.

        :param type_name:  Contains to required information to dump language specific code.
        :type type_name:   DumpInfo

        :return: Dumped type string.
        :rtype:  str
        """
        raise Exception('_dump method not implemented')
