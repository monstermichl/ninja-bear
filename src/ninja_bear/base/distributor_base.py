from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Tuple
from pathlib import Path

from .distribute_info import DistributeInfo
from .distributor_credentials import DistributorCredentials


class DistributorBase(ABC):
    """
    Abstract class that acts as the base for all Distributor implementations. Distributors
    are used to distribute the generated configs to different locations (based on the actual
    distributor implementation).
    """

    def __init__(self, config: Dict, credentials: DistributorCredentials=None):
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
    
    def distribute(self, file_name: str, data: str, input_path: Path):
        """
        Distributes the config according to the derivative implementation.

        :param file_name:  Config file name.
        :type file_name:   str
        :param data:       Config file data.
        :type data:        str
        :param input_path: Input file path.
        :type input_path:  Path

        :return: The current instance.
        :rtype:  DistributorBase
        """
        self._distribute(DistributeInfo(
            file_name=file_name,
            data=data,
            input_path=input_path,
            credentials=self._credentials,
        ))
        return self

    @abstractmethod
    def _distribute(self, info: DistributeInfo):

        """
        Method to distribute a generated config which must be implemented by a derivative class.

        :param info: Contains the required information to distribute the generated config.
        :type info:  DistributeInfo
        """
        pass
