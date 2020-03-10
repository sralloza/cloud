import platform
from pathlib import Path
import json


class _Config:
    LOG_PATH = Path(__file__).parent.with_name("web.log")
    CLOUD_PATH = Path(__file__).parent.with_name("cloud")
    SUDOERS_PATH = Path(__file__).parent.with_name("sudoers.json")
    IGNORED_PATH = Path(__file__).parent.with_name("ignored.json")
    PLATFORM = ""

    @staticmethod
    def setup_config():
        cfg.LOG_PATH.touch()
        cfg.CLOUD_PATH.mkdir(exist_ok=True)
        cfg.SUDOERS_PATH.touch()

        if not cfg.IGNORED_PATH.exists():
            cfg.IGNORED_PATH.write_text(json.dumps(list()))


class _Windows(_Config):
    PLATFORM = "Windows"


class _Linux(_Config):
    PLATFORM = "Linux"


def get_current_config():
    if platform.system() == "Linux":
        return _Linux()
    else:
        return _Windows()


cfg = get_current_config()
cfg.setup_config()
