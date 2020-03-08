import platform
from pathlib import Path
import json


class _Config:
    LOG_PATH = Path(__file__).parent.with_name("web.log")
    CLOUD_PATH = Path(__file__).parent.with_name("files")
    SUDOERS_PATH = Path(__file__).parent.with_name("sudoers.json")
    HIDE_PATH = Path(__file__).parent.with_name("hide.json")
    PLATFORM = ""

    @staticmethod
    def setup_config():
        cfg.LOG_PATH.touch()
        cfg.CLOUD_PATH.mkdir(exist_ok=True)
        cfg.SUDOERS_PATH.touch()

        if not cfg.HIDE_PATH.exists():
            cfg.HIDE_PATH.write_text(json.dumps(list()))


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
