from dataclasses import dataclass
from .distributor_credentials import DistributorCredentials


@dataclass  # https://stackoverflow.com/a/70259423
class DistributeInfo:
    file_name: str
    data: str
    config_path: str
    credentials: DistributorCredentials
