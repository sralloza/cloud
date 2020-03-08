import platform
from pathlib import Path
import json

class _Config:
    LOG_PATH = Path("")
    CLOUD_PATH = Path("")
    SUDOERS_PATH = Path("")
    PLATFORM = ""
    HIDE_PATH = Path("")

    @staticmethod
    def setup_config():
        cfg.LOG_PATH.touch()
        cfg.CLOUD_PATH.mkdir(exist_ok=True)
        cfg.SUDOERS_PATH.touch()

        if not cfg.HIDE_PATH.exists():
            cfg.HIDE_PATH.write_text(json.dumps(list()))


class _Windows(_Config):
    LOG_PATH = Path("D:\\.scripts\\cloud\\web.log")
    CLOUD_PATH = Path("D:\\.scripts\\cloud\\files")
    SUDOERS_PATH = Path("D:\\.scripts\\cloud\\sudoers.json")
    HIDE_PATH = Path("D:\\.scripts\\cloud\\hide.json")
    PLATFORM = "Windows"


class _Linux(_Config):
    LOG_PATH = Path("/srv/cloud/web.log")
    CLOUD_PATH = Path("/srv/cloud/files")
    SUDOERS_PATH = Path("/srv/cloud/sudoers.json")
    HIDE_PATH = Path("/srv/cloud/hide.json")
    PLATFORM = "Linux"


def get_current_config():
    if platform.system() == "Linux":
        return _Linux()
    else:
        return _Windows()


cfg = get_current_config()
cfg.setup_config()
