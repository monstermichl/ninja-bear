class NoAliasProvidedException(Exception):
    def __init__(self):
        super().__init__('No alias has been provided')


class DistributorCredentials:
    """
    Class to encapsulate credentials for specific distributor types.
    """

    distributor_alias: str
    user: str
    password: str

    def __init__(self, distributor_alias: str, user: str='', password: str=''):
        """
        DistributorBase constructor.

        :param distributor_alias: Alias to identify the credentials.
        :type distributor_alias:  str
        :param user:              Credential user, defaults to ''
        :type user:               str, optional
        :param password:          Credential password, defaults to ''
        :type password:           str, optional

        :raises NoAliasProvidedException: Raised if no distribution alias has been provided.
        """
        # Make sure there's an alias for the credentials.
        if not distributor_alias:
            raise NoAliasProvidedException()

        self.distributor_alias = distributor_alias
        self.user = user
        self.password = password
