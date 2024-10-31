from dataclasses import dataclass
from pathlib import Path

from .distributor_credentials import DistributorCredentials


@dataclass  # https://stackoverflow.com/a/70259423
class DistributeInfo:
    file_name: str
    data: str
    input_path: Path
    credentials: DistributorCredentials
