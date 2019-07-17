import json
import warnings

from .config import cfg


class SudoersWarning(Warning):
    pass


def get_sudoers():
    try:
        with cfg.SUDOERS_PATH.open() as f:
            return json.load(f)
    except json.JSONDecodeError as err:
        warnings.warn(f'json decode error: {err}', SudoersWarning)
        return []
    except FileNotFoundError:
        warnings.warn('Sudoers file not found', SudoersWarning)
        return []
