import platform
from pathlib import Path


class _Config:
    LOG_PATH = Path('')
    CLOUD_PATH = Path('')
    SUDOERS_PATH = Path('')
    PLATFORM = ''

    @staticmethod
    def setup_config():
        cfg.LOG_PATH.touch()
        cfg.CLOUD_PATH.mkdir(exist_ok=True)
        cfg.SUDOERS_PATH.touch()


class _Windows(_Config):
    LOG_PATH = Path('D:\\.scripts\\cloud\\web.log')
    CLOUD_PATH = Path('D:\\.scripts\\cloud\\files')
    SUDOERS_PATH = Path('D:\\.scripts\\cloud\\sudoers.json')
    PLATFORM = 'Windows'


class _Linux(_Config):
    LOG_PATH = Path('/srv/cloud/web.log')
    CLOUD_PATH = Path('/srv/cloud/files')
    SUDOERS_PATH = Path('/srv/cloud/sudoers.json')
    PLATFORM = 'Linux'


def get_current_config():
    if platform.system() == 'Linux':
        return _Linux()
    else:
        return _Windows()


cfg = get_current_config()
cfg.setup_config()
