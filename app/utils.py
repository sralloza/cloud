import json
import warnings

from .config import config


class SudoersWarning(Warning):
    pass


def get_sudoers():
    with config.SUDOERS_PATH.open() as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as err:
            warnings.warn(f'json decode error: {err}', SudoersWarning)
            return []
        except FileNotFoundError:
            warnings.warn('Sudoers file not found', SudoersWarning)
            return []
