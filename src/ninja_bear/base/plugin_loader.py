from enum import IntEnum, auto
import pkgutil
import re
from typing import List, Type

from .distributor_base import DistributorBase


class PluginType(IntEnum):
    DISTRIBUTOR = auto()


class Plugin:
    def __init__(self, name: str, type: PluginType, class_type: Type) -> None:
        self._name = name
        self._type = type
        self._class_type = class_type

    def get_name(self) -> str:
        return self._name
    
    def get_type(self) -> PluginType:
        return self._type
    
    def get_class_type(self) -> Type:
        return self._class_type


class PluginLoader:
    def __init__(self) -> None:
        self._modules = [m for m in pkgutil.iter_modules() if re.match('ninja-bear-.+', m.name)]

    def load_distributors(self) -> List[Type[DistributorBase]]:
        return self._load_plugins(PluginType.DISTRIBUTOR, 'Distributor')

    def _load_plugins(self, type: PluginType, class_name: str) -> List[Plugin]:
        plugins = []

        for module in self._modules:
            loaded_module = __import__(module.name)
            plugin = getattr(loaded_module, class_name)

            if plugin:
                plugins.append(Plugin(module.name, type, plugin))
        return plugins
