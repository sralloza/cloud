import json
import warnings
from time import asctime

from flask import request

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


def log(string, *args):
    timestamp = f'[{asctime()}] - {request.remote_addr} - '
    with config.LOG_PATH.open('at') as f:
        f.write(timestamp + string % args + '\n')


def get_user():
    auth = request.authorization
    if not auth:
        return None
    else:
        return auth.username
