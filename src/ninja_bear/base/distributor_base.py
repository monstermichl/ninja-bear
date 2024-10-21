from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict

from .distribute_info import DistributeInfo


class NoAliasProvidedException(Exception):
    def __init__(self):
        super().__init__('No alias has been provided')


class DistributorCredentials:
    """
    Class to encapsulate credentials for specific distributor types.
    """

    distribution_alias: str
    user: str
    password: str

    def __init__(self, distribution_alias: str, user: str='', password: str=''):
        """
        DistributorBase constructor.

        :param distribution_alias: Alias to identify the credentials.
        :type distribution_alias:  str
        :param user:               Credential user, defaults to ''
        :type user:                str, optional
        :param password:           Credential password, defaults to ''
        :type password:            str, optional

        :raises NoAliasProvidedException: Raised if no distribution alias has been provided.
        """
        # Make sure there's an alias for the credentials.
        if not distribution_alias:
            raise NoAliasProvidedException()

        self.distribution_alias = distribution_alias
        self.user = user
        self.password = password


class DistributorBase(ABC):
    """
    Abstract class that acts as the base for all Distributor implementations. Distributors
    are used to distribute the generated configs to different locations (based on the actual
    distributor implementation).
    """

    def __init__(self, config: Dict, credentials: DistributorCredentials=None) -> DistributorBase:
        super().__init__()

        self._config = config
        self._credentials = credentials

    def from_config(self, key: str):
        return self._config[key] if key in self._config else None

    @abstractmethod
    def distribute(self, info: DistributeInfo) -> DistributorBase:

        """
        Method to distribute a generated config which must be implemented by a derivative class.

        :param info: Contains the required information to distribute the generated config.
        :type info:  DistributeInfo
        """
        pass
