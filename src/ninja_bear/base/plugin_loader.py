from enum import IntEnum, auto
from importlib.metadata import entry_points
import re
from typing import List, Type

from .distributor_base import DistributorBase
from .language_config_base import LanguageConfigBase


class PluginType(IntEnum):
    UNKNOWN = 0,
    LANGUAGE_CONFIG = auto()
    DISTRIBUTOR = auto()


class Plugin:
    def __init__(self, name: str, class_type: Type) -> None:
        self._name = name
        self._class_type = class_type

        plugin_type = PluginType.UNKNOWN

        # Specify plugin type by base-class.
        if self._is_language_plugin(class_type):
            plugin_type = PluginType.LANGUAGE_CONFIG
        elif self._is_distributor_plugin(class_type):
            plugin_type = PluginType.DISTRIBUTOR
        self._type = plugin_type

    def get_name(self) -> str:
        return self._name
    
    def get_type(self) -> PluginType:
        return self._type
    
    def get_class_type(self) -> Type:
        return self._class_type
    
    def _inherits(self, check_type: Type, check_class: Type):
        base_classes_names = list(map(lambda clazz: clazz.__name__, check_class.__bases__))
        return check_type.__name__ in base_classes_names
    
    def _is_language_plugin(self, check_class: Type):
        return self._inherits(LanguageConfigBase, check_class)
    
    def _is_distributor_plugin(self, check_class: Type):
        return self._inherits(DistributorBase, check_class)


class PluginLoader:
    def __init__(self, additional_plugins: List[Plugin]=[]) -> None:
        self._plugins = []

        self._load_plugins()
        self.add_plugins(additional_plugins)

    def add_plugins(self, plugins: List[Plugin]):
        self._plugins.extend([p for p in plugins if p and p.get_type() != PluginType.UNKNOWN])

    def get_plugins(self) -> List[Type[Plugin]]:
        return self._plugins

    def get_language_config_plugins(self) -> List[Type[Plugin]]:
        return self._get_plugins_by_type(PluginType.LANGUAGE_CONFIG)

    def get_distributor_plugins(self) -> List[Type[Plugin]]:
        return self._get_plugins_by_type(PluginType.DISTRIBUTOR)
    
    def _get_plugins_by_type(self, type: PluginType):
        return [plugin for plugin in self._plugins if plugin.get_type() == type]

    def _load_plugins(self):
        plugins = []

        for entry_point in [e for e in entry_points() if re.match('ninja-bear-.+', e.group)]:
            plugin_class = entry_point.load()

            if plugin_class:
                plugins.append(Plugin(entry_point.group, plugin_class))
        self.add_plugins(plugins)
