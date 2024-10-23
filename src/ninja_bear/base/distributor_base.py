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

    def from_config(self, key: str):
        return self._config[key] if key in self._config else None
    
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
