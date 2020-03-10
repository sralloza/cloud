import warnings

import pytest

from app.utils.exceptions import CloudError, CloudWarning, IngoredWarning, SudoersWarning


class TestCloudError:
    def test_inheritance(self):
        exc = CloudError()
        assert isinstance(exc, CloudError)
        assert isinstance(exc, Exception)

    def test_raise(self):
        with pytest.raises(CloudError):
            raise CloudError


class TestCloudWarning:
    def test_inheritance(self):
        warn = CloudWarning()
        assert isinstance(warn, CloudWarning)
        assert isinstance(warn, Warning)

    def test_raise(self):
        with pytest.warns(CloudWarning):
            warnings.warn("message", CloudWarning)


class TestSudoersWarning:
    def test_inheritance(self):
        warn = SudoersWarning()
        assert isinstance(warn, SudoersWarning)
        assert isinstance(warn, CloudWarning)

    def test_raise(self):
        with pytest.warns(SudoersWarning):
            warnings.warn("message", SudoersWarning)


class TestIngoredWarning:
    def test_inheritance(self):
        warn = IngoredWarning()
        assert isinstance(warn, IngoredWarning)
        assert isinstance(warn, CloudWarning)

    def test_raise(self):
        with pytest.warns(IngoredWarning):
            warnings.warn("message", IngoredWarning)
