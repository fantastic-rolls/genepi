import os
from configparser import ConfigParser
from importlib.resources import files
from typing import Optional

from typing_extensions import Self

import genepi.data
from genepi.utils import Singleton


def int_value(value: Optional[str], default: int = 0) -> int:
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


class Configuration(metaclass=Singleton):
    def __init__(self, conf: Optional[ConfigParser]) -> None:
        if conf is None:
            conf = ConfigParser()

        self.panel_duration = conf.getint("panels", "duration", fallback=10)
        self.transitions = {}

        for key, value in conf.items("transitions"):
            self.transitions[key] = value

        self.after_effects_template = conf.get("templates", "after_effects")

    @classmethod
    def load_config(cls, config_path: Optional[str] = None) -> Self:
        if config_path is None:
            config_path = os.path.join(os.getenv("HOME"), ".genepi.conf")
            if not os.path.exists(config_path):
                config = files(genepi.data).joinpath("default.conf").read_text()
                with open(config_path, "w", encoding="utf-8") as fp:
                    fp.write(config)

            config_parser = ConfigParser()
            config_parser.read(config_path)
            return Configuration(config_parser)


cfg = Configuration.load_config(None)
print(cfg)
