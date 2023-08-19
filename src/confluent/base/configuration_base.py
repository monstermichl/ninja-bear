_DEFAULT_INDENT = 4


class ConfigurationBase:
    """
    Serves as the base for several configuration classes.
    """
    indent: int = _DEFAULT_INDENT
    transform: str
