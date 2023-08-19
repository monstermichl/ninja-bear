_DEFAULT_INDENT = 4


class ConfigurationBase:
    """
    Serves as the base for several configuration classes.
    """
    indent: int = _DEFAULT_INDENT
    """
    Whitespace indent before each property, defaults to _DEFAULT_INDENT
    """
    transform: str
    """
    Python function which can transform the provided value.
    """
