import json
import platform
from os import path
from pathlib import Path


class Configurations:
    def __init__(self):
        self._conf = {}
        self._conf_path = self.__class__.get_config_path()

        self.load_configs()

    @staticmethod
    def get_config_path():
        if platform.system() == "Windows":
            return Path(path.expandvars("%APPDATA%/Emulsion/.config.json"))
        else:
            return Path(path.expanduser("~/.emulsion"))

    def save_configs(self):
        with open(self._conf_path, "w") as f:
            json.dump(self._conf, f)

    def load_configs(self):
        if not self._conf_path.exists():
            self._conf_path.parent.mkdir(parents=True, exist_ok=True)
            self._conf_path.touch(exist_ok=True)
            self.save_configs()
        else:
            with open(self._conf_path, "r") as f:
                self._conf = json.load(f)

    def get_token(self):
        return self._conf.get("token", None)

    def save_token(self, token):
        self._conf["token"] = token
        self.save_configs()
