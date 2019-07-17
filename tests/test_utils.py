import warnings
from datetime import datetime
from unittest import mock

import pytest

from app.utils import SudoersWarning, get_sudoers, log


def test_warning():
    with pytest.warns(SudoersWarning):
        warnings.warn('Sudoers Warning', SudoersWarning)


@mock.patch('app.utils.cfg')
def test_get_sudoers(mocker):
    fp = mocker.SUDOERS_PATH.open.return_value.__enter__.return_value
    fp.read.return_value = '["user_a"]'
    assert get_sudoers() == ['user_a']

    with pytest.warns(SudoersWarning, match='json decode error'):
        fp.read.return_value = 'invalid'
        assert get_sudoers() == []

    with pytest.warns(SudoersWarning, match='Sudoers file not found'):
        fp.read.side_effect = FileNotFoundError
        assert get_sudoers() == []


@mock.patch('app.utils.cfg', spec=True)
@mock.patch('app.utils.request', spec=True)
@mock.patch('app.utils.asctime', spec=True)
def test_log(asctime_mock, request_mock, cfg_mock):
    str_time = datetime(2019, 1, 1).ctime()
    asctime_mock.return_value = str_time
    request_mock.remote_addr = '10.0.0.1'
    fp = cfg_mock.LOG_PATH.open.return_value.__enter__.return_value

    args = f'[{str_time}] - 10.0.0.1 - hello-world\n'

    log('hello-world')
    asctime_mock.assert_called_once()
    fp.write.assert_called_once_with(args)

    log('a=%s, b=%r, c=%03d', 'letter-a', 'letter-b', 10)
    args = f"[{str_time}] - 10.0.0.1 - a=letter-a, b='letter-b', c=010\n"

    assert asctime_mock.call_count == 2
    fp.write.assert_called_with(args)
    assert fp.write.call_count == 2
