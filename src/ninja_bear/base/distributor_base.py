from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict

from .distribute_info import DistributeInfo
from .distributor_credentials import DistributorCredentials


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

    def from_config(self, key: str) -> Tuple[any, bool]:
        """
        Retrieves a value from the distributor config. If the key doesn't exist,
        None is returned.

        :param key: Value key.
        :type key:  str

        :return: Returns a tuple where the first entry is the value and the second
                 a boolean which states if the key exists.
        :rtype:  (any, bool)
        """
        key_exists = key in self._config

        return self._config[key] if key_exists else None, key_exists
    
    def distribute(self, file_name: str, data: str) -> DistributorBase:
        return self._distribute(DistributeInfo(
            file_name,
            data,
            self._credentials,
        ))

    @abstractmethod
    def _distribute(self, info: DistributeInfo) -> DistributorBase:

        """
        Method to distribute a generated config which must be implemented by a derivative class.

        :param info: Contains the required information to distribute the generated config.
        :type info:  DistributeInfo
        """
        pass
