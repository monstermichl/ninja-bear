from dataclasses import dataclass


@dataclass(kw_only=True)  # https://stackoverflow.com/a/70259423
class MetaDataSettings:
    user: bool = False
    date: bool = False
    time: bool = False
    version: bool = False
    link: bool = False
