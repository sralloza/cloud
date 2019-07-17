import json
import os
import warnings
from pathlib import Path
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


def get_folders():
    folder_choices = [Path(x[0]).relative_to(cfg.CLOUD_PATH) for x in os.walk(cfg.CLOUD_PATH)]

    if get_user() not in get_sudoers():
        def filter_choice(x):
            return not (x.as_posix().startswith('.') and len(x.as_posix()) > 1)

        folder_choices = [x for x in folder_choices if filter_choice(x)]

    folder_choices.sort()
    return folder_choices
