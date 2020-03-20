import json
import sys
import warnings
from datetime import datetime
from unittest import mock

import pytest

from app.utils import (
    add_to_ignored,
    gen_random_password,
    get_folders,
    get_ignored,
    get_post_arg,
    get_sudoers,
    get_user,
    log,
    remove_from_ignored,
)
from app.utils.exceptions import IngoredWarning, SudoersWarning


def test_warning():
    with pytest.warns(SudoersWarning):
        warnings.warn("Sudoers Warning", SudoersWarning)


@mock.patch("app.utils.cfg")
def test_get_sudoers(mocker):
    fp = mocker.SUDOERS_PATH.open.return_value.__enter__.return_value
    fp.read.return_value = '["user_a"]'
    assert get_sudoers() == ["user_a"]

    with pytest.warns(SudoersWarning, match="json decode error"):
        fp.read.return_value = "invalid"
        assert get_sudoers() == []

    with pytest.warns(SudoersWarning, match="Sudoers file not found"):
        fp.read.side_effect = FileNotFoundError
        assert get_sudoers() == []


@mock.patch("app.utils.cfg.IGNORED_PATH")
class TestGetignored:
    def test_normal(self, ign_path_m):
        data = ["bbb", "aaa"]
        ign_path_m.read_text.return_value = json.dumps(data * 5)

        ignored = get_ignored()
        data.sort()
        assert ignored == data

    def test_error(self, ign_path_m):
        ign_path_m.read_text.return_value = ""

        with pytest.warns(IngoredWarning):
            ignored = get_ignored()
        assert ignored == []


@mock.patch("app.utils.cfg.IGNORED_PATH")
@mock.patch("app.utils.get_ignored")
class TestAddToignored:
    def test_true(self, ign_m, ign_path_m):
        ign_m.return_value = ["aaa", "bbb"]
        result = add_to_ignored("ccc")

        expected_call = json.dumps(["aaa", "bbb", "ccc"], indent=4)
        assert result is True
        ign_path_m.write_text.assert_called_once_with(expected_call)

    def test_false(self, ign_m, ign_path_m):
        ign_m.return_value = ["aaa", "bbb", "ccc"]
        result = add_to_ignored("ccc")

        assert result is False
        ign_path_m.write_text.assert_not_called()


@mock.patch("app.utils.cfg.IGNORED_PATH")
@mock.patch("app.utils.get_ignored")
class TestRemoveFromignored:
    def test_true(self, ign_m, ign_path_m):
        ign_m.return_value = ["aaa", "bbb", "ccc"]
        result = remove_from_ignored("ccc")

        expected_call = json.dumps(["aaa", "bbb"], indent=4)
        assert result is True
        ign_path_m.write_text.assert_called_once_with(expected_call)

    def test_false(self, ign_m, ign_path_m):
        ign_m.return_value = ["aaa", "bbb"]
        result = remove_from_ignored("ccd")

        assert result is False
        ign_path_m.write_text.assert_not_called()


@pytest.mark.skipif(sys.platform != "win32", reason="Does not work on linux")
@mock.patch("app.utils.cfg", spec=True)
@mock.patch("app.utils.request", spec=True)
@mock.patch("app.utils.asctime", spec=True)
def test_log(asc_m, req_m, cfg_m):
    str_time = datetime(2019, 1, 1).ctime()
    asc_m.return_value = str_time
    req_m.remote_addr = "10.0.0.1"
    fp = cfg_m.LOG_PATH.open.return_value.__enter__.return_value

    args = f"[{str_time}] - 10.0.0.1 - hello-world\n"

    log("hello-world")
    asc_m.assert_called_once()
    fp.write.assert_called_once_with(args)

    log("a=%s, b=%r, c=%03d", "letter-a", "letter-b", 10)
    args = f"[{str_time}] - 10.0.0.1 - a=letter-a, b='letter-b', c=010\n"

    assert asc_m.call_count == 2
    fp.write.assert_called_with(args)
    assert fp.write.call_count == 2


@pytest.mark.skipif(sys.platform != "win32", reason="Does not work on linux")
@mock.patch("app.utils.request", spec=True)
class TestGetUser:
    def test_no_authorization(self, req_m):
        req_m.authorization = None
        assert get_user() is None

    def test_normal_authorization(self, req_m):
        req_m.authorization = mock.Mock(username="foo")
        assert get_user() == "foo"

    def test_runtime_error(self, req_m):
        prop_m = mock.PropertyMock()
        prop_m.side_effect = RuntimeError
        type(req_m).authorization = prop_m
        assert get_user() is None


class TestGetFolders:
    def setup_class(self):
        self.input_data = (
            ("/test/folder-1",),
            ("/test/folder-1/subfolder-1.2/subsubfolder-1.2.1",),
            ("/test/folder-1/subfolder-1.1",),
            ("/test/folder-1/subfolder-1.2",),
            ("/test/folder-2",),
            ("/test/folder-2/subfolder-2.1",),
            ("/test/.data/something",),
        )
        self.output_data = (
            ".data/something",
            "folder-1",
            "folder-1/subfolder-1.1",
            "folder-1/subfolder-1.2",
            "folder-1/subfolder-1.2/subsubfolder-1.2.1",
            "folder-2",
            "folder-2/subfolder-2.1",
        )

    @pytest.fixture(scope="function", autouse=True)
    def mocks(self):
        self.cfg_m = mock.patch("app.utils.cfg", spec=True).start()
        self.walk_m = mock.patch("os.walk", spec=True).start()
        self.gu_m = mock.patch("app.utils.get_user", spec=True).start()
        self.sud_m = mock.patch("app.utils.get_sudoers", spec=True).start()
        self.ign_m = mock.patch("app.utils.get_ignored", spec=True).start()

        yield

        mock.patch.stopall()

    def test_no_sudores_or_ignored(self):
        self.cfg_m.CLOUD_PATH = "/test"
        self.walk_m.return_value = self.input_data
        self.gu_m.return_value = None
        self.sud_m.return_value = []
        self.ign_m.return_value = []

        expected = self.output_data[1:]
        real = tuple([x.as_posix() for x in get_folders()])

        assert real == expected

    def test_sudoers(self):
        self.cfg_m.CLOUD_PATH = "/test"
        self.walk_m.return_value = self.input_data
        self.gu_m.return_value = "user"
        self.sud_m.return_value = ["user"]
        self.ign_m.return_value = []

        expected = self.output_data
        real = tuple([x.as_posix() for x in get_folders()])

        assert real == expected

    def test_ignored(self):
        self.cfg_m.CLOUD_PATH = "/test"
        self.walk_m.return_value = self.input_data
        self.gu_m.return_value = "user"
        self.sud_m.return_value = []
        self.ign_m.return_value = ["folder-2"]

        expected = self.output_data[1:-2]
        real = tuple([x.as_posix() for x in get_folders()])

        assert real == expected


def test_gen_random_password():
    p1 = gen_random_password()
    p2 = gen_random_password()
    p3 = gen_random_password()

    assert p1 != p2 != p3
    assert len(p1) == len(p2) == len(p3) == 16

    p4 = gen_random_password(n=24)
    assert len(p4) == 24


@pytest.mark.skipif(sys.platform != "win32", reason="Does not work on linux")
@mock.patch("app.utils.request", autospec=True)
class TestGetPostArg:
    data_req_strip = (
        ({"data": "value"}, "value"),
        ({"data": "  value  "}, "value"),
        ({"data": "  value  \n"}, "value"),
        ({"data": ""}, RuntimeError),
        ({"data": "  "}, RuntimeError),
        ({"data": " \n\n "}, RuntimeError),
        ({}, RuntimeError),
    )

    data_not_req_strip = (
        ({"data": "value"}, "value"),
        ({"data": "  value  "}, "value"),
        ({"data": "  value  \n"}, "value"),
        ({"data": ""}, None),
        ({"data": "  "}, None),
        ({"data": " \n\n "}, None),
        ({}, None),
    )

    data_req_not_strip = (
        ({"data": "value"}, "value"),
        ({"data": "  value  "}, "  value  "),
        ({"data": "  value  \n"}, "  value  \n"),
        ({"data": ""}, RuntimeError),
        ({"data": "  "}, "  "),
        ({"data": " \n\n "}, " \n\n "),
        ({}, RuntimeError),
    )

    data_not_req_not_strip = (
        ({"data": "value"}, "value"),
        ({"data": "  value  "}, "  value  "),
        ({"data": "  value  \n"}, "  value  \n"),
        ({"data": ""}, ""),
        ({"data": "  "}, "  "),
        ({"data": " \n\n "}, " \n\n "),
        ({}, None),
    )

    @pytest.mark.parametrize("request_data, expected", data_req_strip)
    def test_req_strip(self, req_m, request_data, expected):
        req_m.form = request_data
        if expected == RuntimeError:
            with pytest.raises(expected):
                get_post_arg("data", required=True, strip=True)
        else:
            assert get_post_arg("data", required=True, strip=True) == expected

    @pytest.mark.parametrize("request_data, expected", data_not_req_strip)
    def test_not_req_strip(self, req_m, request_data, expected):
        req_m.form = request_data
        assert get_post_arg("data", required=False, strip=True) == expected

    @pytest.mark.parametrize("request_data, expected", data_req_not_strip)
    def test_req_not_strip(self, req_m, request_data, expected):
        req_m.form = request_data
        if expected == RuntimeError:
            with pytest.raises(expected):
                get_post_arg("data", required=True, strip=False)
        else:
            assert get_post_arg("data", required=True, strip=False) == expected

    @pytest.mark.parametrize("request_data, expected", data_not_req_not_strip)
    def test_not_req_not_strip(self, req_m, request_data, expected):
        req_m.form = request_data
        assert get_post_arg("data", required=False, strip=False) == expected
