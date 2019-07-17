import json
import warnings
from time import asctime

from flask import request

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


def log(string, *args):
    timestamp = f'[{asctime()}] - {request.remote_addr} - '
    with cfg.LOG_PATH.open('at') as f:
        f.write(timestamp + string % args + '\n')


def get_user():
    auth = request.authorization
    if not auth:
        return None
    else:
        return auth.username
