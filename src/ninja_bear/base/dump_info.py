from dataclasses import dataclass
from typing import Dict, List
from .property import Property


@dataclass  # https://stackoverflow.com/a/70259423
class DumpInfo:
    type_name: str
    properties: List[Property]
    indent: int
    additional_props: Dict
