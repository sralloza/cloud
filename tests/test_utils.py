import json
import warnings
from datetime import datetime
from unittest import mock

import pytest

from app.utils import (HidesWarning, SudoersWarning, add_to_hides,
                       gen_random_password, get_folders, get_hides,
                       get_post_arg, get_sudoers, get_user, log,
                       remove_from_hides)


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


@mock.patch("app.utils.cfg.HIDE_PATH")
class TestGetHides:
    def test_normal(self, hide_path_mock):
        data = ["bbb", "aaa"]
        hide_path_mock.read_text.return_value = json.dumps(data * 5)

        hides = get_hides()
        data.sort()
        assert hides == data

    def test_error(self, hide_path_mock):
        hide_path_mock.read_text.return_value = ""

        with pytest.warns(HidesWarning):
            hides = get_hides()
        assert hides == []


@mock.patch("app.utils.cfg.HIDE_PATH")
@mock.patch("app.utils.get_hides")
class TestAddToHides:
    def test_true(self, hides_mock, hide_path_mock):
        hides_mock.return_value = ["aaa", "bbb"]
        result = add_to_hides("ccc")

        expected_call = json.dumps(["aaa", "bbb", "ccc"], indent=4)
        assert result is True
        hide_path_mock.write_text.assert_called_once_with(expected_call)

    def test_false(self, hides_mock, hide_path_mock):
        hides_mock.return_value = ["aaa", "bbb", "ccc"]
        result = add_to_hides("ccc")

        assert result is False
        hide_path_mock.write_text.assert_not_called()


@mock.patch("app.utils.cfg.HIDE_PATH")
@mock.patch("app.utils.get_hides")
class TestRemoveFromHides:
    def test_true(self, hides_mock, hide_path_mock):
        hides_mock.return_value = ["aaa", "bbb", "ccc"]
        result = remove_from_hides("ccc")

        expected_call = json.dumps(["aaa", "bbb"], indent=4)
        assert result is True
        hide_path_mock.write_text.assert_called_once_with(expected_call)

    def test_false(self, hides_mock, hide_path_mock):
        hides_mock.return_value = ["aaa", "bbb"]
        result = remove_from_hides("ccd")

        assert result is False
        hide_path_mock.write_text.assert_not_called()


@mock.patch("app.utils.cfg", spec=True)
@mock.patch("app.utils.request", spec=True)
@mock.patch("app.utils.asctime", spec=True)
def test_log(asctime_mock, request_mock, cfg_mock):
    str_time = datetime(2019, 1, 1).ctime()
    asctime_mock.return_value = str_time
    request_mock.remote_addr = "10.0.0.1"
    fp = cfg_mock.LOG_PATH.open.return_value.__enter__.return_value

    args = f"[{str_time}] - 10.0.0.1 - hello-world\n"

    log("hello-world")
    asctime_mock.assert_called_once()
    fp.write.assert_called_once_with(args)

    log("a=%s, b=%r, c=%03d", "letter-a", "letter-b", 10)
    args = f"[{str_time}] - 10.0.0.1 - a=letter-a, b='letter-b', c=010\n"

    assert asctime_mock.call_count == 2
    fp.write.assert_called_with(args)
    assert fp.write.call_count == 2


@mock.patch("app.utils.request", spec=True)
class TestGetUser:
    def test_no_authorization(self, request_mock):
        request_mock.authorization = None
        assert get_user() is None

    def test_normal_authorization(self, request_mock):
        request_mock.authorization = mock.Mock(username="foo")
        assert get_user() == "foo"

    def test_runtime_error(self, request_mock):
        prop_mock = mock.PropertyMock()
        prop_mock.side_effect = RuntimeError
        type(request_mock).authorization = prop_mock
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

    @pytest.fixture
    def folders_mocker(self):
        cfg_mock = mock.patch("app.utils.cfg", spec=True).start()
        os_walk_mock = mock.patch("os.walk", spec=True).start()
        get_user_mock = mock.patch("app.utils.get_user", spec=True).start()
        sudoers_mock = mock.patch("app.utils.get_sudoers", spec=True).start()
        hides_mock = mock.patch("app.utils.get_hides", spec=True).start()

        yield cfg_mock, os_walk_mock, get_user_mock, sudoers_mock, hides_mock

        mock.patch.stopall()

    def test_no_sudores_or_hides(self, folders_mocker):
        cfg_mock, os_walk_mock, get_user_mock, sudoers_mock, hides_mock = folders_mocker

        cfg_mock.CLOUD_PATH = "/test"
        os_walk_mock.return_value = self.input_data
        get_user_mock.return_value = None
        sudoers_mock.return_value = []
        hides_mock.return_value = []

        expected = self.output_data[1:]
        real = tuple([x.as_posix() for x in get_folders()])

        assert real == expected

    def test_sudoers(self, folders_mocker):
        cfg_mock, os_walk_mock, get_user_mock, sudoers_mock, hides_mock = folders_mocker

        cfg_mock.CLOUD_PATH = "/test"
        os_walk_mock.return_value = self.input_data
        get_user_mock.return_value = "user"
        sudoers_mock.return_value = ["user"]
        hides_mock.return_value = []

        expected = self.output_data
        real = tuple([x.as_posix() for x in get_folders()])

        assert real == expected

    def test_hides(self, folders_mocker):
        cfg_mock, os_walk_mock, get_user_mock, sudoers_mock, hides_mock = folders_mocker

        cfg_mock.CLOUD_PATH = "/test"
        os_walk_mock.return_value = self.input_data
        get_user_mock.return_value = "user"
        sudoers_mock.return_value = []
        hides_mock.return_value = ["folder-2"]

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
    def test_req_strip(self, request_mock, request_data, expected):
        request_mock.form = request_data
        if expected == RuntimeError:
            with pytest.raises(expected):
                get_post_arg("data", required=True, strip=True)
        else:
            assert get_post_arg("data", required=True, strip=True) == expected

    @pytest.mark.parametrize("request_data, expected", data_not_req_strip)
    def test_not_req_strip(self, request_mock, request_data, expected):
        request_mock.form = request_data
        assert get_post_arg("data", required=False, strip=True) == expected

    @pytest.mark.parametrize("request_data, expected", data_req_not_strip)
    def test_req_not_strip(self, request_mock, request_data, expected):
        request_mock.form = request_data
        if expected == RuntimeError:
            with pytest.raises(expected):
                get_post_arg("data", required=True, strip=False)
        else:
            assert get_post_arg("data", required=True, strip=False) == expected

    @pytest.mark.parametrize("request_data, expected", data_not_req_not_strip)
    def test_not_req_not_strip(self, request_mock, request_data, expected):
        request_mock.form = request_data
        assert get_post_arg("data", required=False, strip=False) == expected
