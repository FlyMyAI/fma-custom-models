import os
from typing import Optional, Self

import yaml
from yaml.loader import Loader

from fma._constants import CONFIG_DIR, CONFIG_PATH
from fma._utils import SingletonMeta


class ConfigManager(metaclass=SingletonMeta):
    __config: dict
    __config_path: str
    __instance: Optional[Self] = None

    def __init__(self):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        self._load_config()

    def reset_config(self):
        self.__config = {}
        self._dump_config()

    def get(self, key, default=None):
        return self.__config.get(key, default) 

    def set(self, key, value):
        self.__config[key] = value
        self._dump_config()

    def remove(self, key):
        del self.__config[key]
        self._dump_config()

    def _load_config(self):
        if not os.path.exists(CONFIG_PATH):
            self.__config = {}
            return
        with open(CONFIG_PATH) as file:
            self.__config = yaml.load(file, Loader)

    def _dump_config(self):
        with open(CONFIG_PATH, "w") as file:
            yaml.safe_dump(self.__config, file, allow_unicode=True)


config_manager = ConfigManager()
