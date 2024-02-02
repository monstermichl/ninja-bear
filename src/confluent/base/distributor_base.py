from __future__ import annotations
from abc import ABC, abstractmethod


class DistributorCredential:
    distribution_alias: str
    user: str
    password: str

    def __init__(self, distribution_alias: str, user: str, password: str):
        self.distribution_alias = distribution_alias
        self.user = user
        self.password = password


class DistributorBase(ABC):

    @abstractmethod
    def distribute(data: str):
        pass
