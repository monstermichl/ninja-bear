from __future__ import annotations
from abc import ABC, abstractmethod


class DistributorBase(ABC):

    @abstractmethod
    def distribute(data: str):
        pass
