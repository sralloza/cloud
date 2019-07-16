import json

from .config import config


def get_sudoers():
    with config.SUDOERS_PATH.open() as f:
        try:
            return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
