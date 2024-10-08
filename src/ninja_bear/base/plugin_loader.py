from enum import IntEnum, auto
from importlib.metadata import entry_points
import re
from typing import List, Type

from .distributor_base import DistributorBase
from .language_config_base import LanguageConfigBase


class PluginType(IntEnum):
    LANGUAGE_CONFIG = 1
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
        self._plugins = self._load_plugins()

    def get_plugins(self) -> List[Type[Plugin]]:
        return self._plugins

    def get_language_config_plugins(self) -> List[Type[Plugin]]:
        return self._get_plugins_by_type(PluginType.LANGUAGE_CONFIG)

    def get_distributor_plugins(self) -> List[Type[Plugin]]:
        return self._get_plugins_by_type(PluginType.DISTRIBUTOR)
    
    def _get_plugins_by_type(self, type: PluginType):
        return [plugin for plugin in self._plugins if plugin.get_type() == type]

    def _load_plugins(self) -> List[Plugin]:
        plugins = []

        def inherits(check_type: Type, check_class: Type):
            base_classes_names = list(map(lambda clazz: clazz.__name__, check_class.__bases__))
            return check_type.__name__ in base_classes_names

        for entry_point in [e for e in entry_points() if re.match('ninja-bear-.+', e.group)]:
            plugin_class = entry_point.load()

            if plugin_class:
                plugin_type = None

                # Specify plugin type by base-class.
                if inherits(LanguageConfigBase, plugin_class):
                    plugin_type = PluginType.LANGUAGE_CONFIG
                elif inherits(DistributorBase, plugin_class):
                    plugin_type = PluginType.DISTRIBUTOR

                if plugin_type:
                    plugins.append(Plugin(entry_point.group, plugin_type, plugin_class))
        return plugins
