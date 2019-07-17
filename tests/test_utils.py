import warnings
from unittest import mock

import pytest

from app.utils import SudoersWarning, get_sudoers


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
