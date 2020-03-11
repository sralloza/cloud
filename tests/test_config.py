from pathlib import Path
from unittest import mock

import pytest

from app.config import _Config, _Linux, _Windows, get_current_config


def test_attributes():
    assert hasattr(_Config, "LOG_PATH")
    assert hasattr(_Config, "CLOUD_PATH")
    assert hasattr(_Config, "SUDOERS_PATH")
    assert hasattr(_Config, "IGNORED_PATH")
    assert hasattr(_Config, "PLATFORM")

    assert hasattr(_Windows, "LOG_PATH")
    assert hasattr(_Windows, "CLOUD_PATH")
    assert hasattr(_Windows, "SUDOERS_PATH")
    assert hasattr(_Windows, "IGNORED_PATH")
    assert hasattr(_Windows, "PLATFORM")

    assert hasattr(_Linux, "LOG_PATH")
    assert hasattr(_Linux, "CLOUD_PATH")
    assert hasattr(_Linux, "SUDOERS_PATH")
    assert hasattr(_Linux, "IGNORED_PATH")
    assert hasattr(_Linux, "PLATFORM")


def test_types():
    assert isinstance(_Config.LOG_PATH, Path)
    assert isinstance(_Config.CLOUD_PATH, Path)
    assert isinstance(_Config.SUDOERS_PATH, Path)
    assert isinstance(_Config.IGNORED_PATH, Path)
    assert isinstance(_Config.PLATFORM, str)

    assert isinstance(_Windows.LOG_PATH, Path)
    assert isinstance(_Windows.CLOUD_PATH, Path)
    assert isinstance(_Windows.SUDOERS_PATH, Path)
    assert isinstance(_Windows.IGNORED_PATH, Path)
    assert isinstance(_Windows.PLATFORM, str)

    assert isinstance(_Linux.LOG_PATH, Path)
    assert isinstance(_Linux.CLOUD_PATH, Path)
    assert isinstance(_Linux.SUDOERS_PATH, Path)
    assert isinstance(_Linux.IGNORED_PATH, Path)
    assert isinstance(_Linux.PLATFORM, str)


def test_get_current_config():
    with mock.patch("platform.system") as mocker:
        mocker.return_value = "Linux"
        assert isinstance(get_current_config(), _Linux)

    with mock.patch("platform.system") as mocker:
        mocker.return_value = "Windows"
        assert isinstance(get_current_config(), _Windows)


@pytest.mark.parametrize("ignored_exists", [True, False])
@mock.patch("platform.system")
def test_setup_config(mocker, ignored_exists):
    mocker.return_value = "Linux"
    assert isinstance(get_current_config(), _Linux)

    with mock.patch("app.config.cfg") as mocker:
        mocker.IGNORED_PATH.exists.return_value = ignored_exists

        get_current_config().setup_config()

        mocker.LOG_PATH.touch.assert_called_once()
        mocker.CLOUD_PATH.mkdir.assert_called_once_with(exist_ok=True)
        mocker.SUDOERS_PATH.touch.assert_called_once()

        if not ignored_exists:
            mocker.IGNORED_PATH.write_text.assert_called_once_with("[]")
        else:
            mocker.IGNORED_PATH.write_text.assert_not_called()


    # TODO: test call for IGNORED_PATH.touch() if it doesn't exist
