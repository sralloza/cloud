import platform
from pathlib import Path


class _Config:
    LOG_PATH = Path('')
    CLOUD_PATH = Path('')
    SUDOERS_PATH = Path('')
    PLATFORM = ''


class _Windows(_Config):
    LOG_PATH = Path('D:\\.scripts\\cloud\\web.log')
    CLOUD_PATH = Path('D:\\.scripts\\cloud\\files')
    SUDOERS_PATH = Path('D:\\.scripts\\cloud\\sudoers.json')
    PLATFORM = 'Windows'


class _Linux(_Config):
    LOG_PATH = Path('/srv/private/web.log')
    CLOUD_PATH = Path('/srv/private/files')
    SUDOERS_PATH = Path('/srv/private/sudoers.json')
    PLATFORM = 'Linux'


if platform.system() == 'Linux':
    config = _Linux()
else:
    config = _Windows()

config.LOG_PATH.touch()
config.CLOUD_PATH.mkdir(exist_ok=True)
