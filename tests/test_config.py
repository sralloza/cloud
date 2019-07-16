from pathlib import Path
from unittest import mock

from app.config import _Linux, _Windows, _Config, get_current_config


def test_attributes():
    assert hasattr(_Config, 'LOG_PATH')
    assert hasattr(_Config, 'CLOUD_PATH')
    assert hasattr(_Config, 'SUDOERS_PATH')
    assert hasattr(_Config, 'PLATFORM')

    assert hasattr(_Windows, 'LOG_PATH')
    assert hasattr(_Windows, 'CLOUD_PATH')
    assert hasattr(_Windows, 'SUDOERS_PATH')
    assert hasattr(_Windows, 'PLATFORM')

    assert hasattr(_Linux, 'LOG_PATH')
    assert hasattr(_Linux, 'CLOUD_PATH')
    assert hasattr(_Linux, 'SUDOERS_PATH')
    assert hasattr(_Linux, 'PLATFORM')


def test_types():
    assert isinstance(_Config.LOG_PATH, Path)
    assert isinstance(_Config.CLOUD_PATH, Path)
    assert isinstance(_Config.SUDOERS_PATH, Path)
    assert isinstance(_Config.PLATFORM, str)

    assert isinstance(_Windows.LOG_PATH, Path)
    assert isinstance(_Windows.CLOUD_PATH, Path)
    assert isinstance(_Windows.SUDOERS_PATH, Path)
    assert isinstance(_Windows.PLATFORM, str)

    assert isinstance(_Linux.LOG_PATH, Path)
    assert isinstance(_Linux.CLOUD_PATH, Path)
    assert isinstance(_Linux.SUDOERS_PATH, Path)
    assert isinstance(_Linux.PLATFORM, str)


def test_get_current_config():
    with mock.patch('platform.system') as mocker:
        mocker.return_value = 'Linux'
        assert isinstance(get_current_config(), _Linux)

    with mock.patch('platform.system') as mocker:
        mocker.return_value = 'Windows'
        assert isinstance(get_current_config(), _Windows)


def test_setup():
    # todo test that touch() and mkdir() are called during import
    pass
