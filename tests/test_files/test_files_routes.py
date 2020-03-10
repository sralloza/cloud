import io
from itertools import product
from pathlib import Path
from unittest import mock

import pytest

FILEPATHS = [
    "hello/world",
    "a/b/c/d/e/f/g",
    "hi/peter/how/are-you.file",
    "simple",
    "complex/$5",
    "p123/cdcdsc/../plt",
    "=sdf)/jk",
    "^d/-_df/asd",
    "(~€_;/.@·![]/´{}ç¿/8",
]


class TestUpload:
    @pytest.fixture(autouse=True)
    def upload_mocks(self):
        folders = [Path(x) for x in ["folder-1", "folder-2", "folder-3"]]

        cfg_mock = mock.patch("app.files.routes.cfg").start()
        file_storage_mock = mock.patch(
            "werkzeug.datastructures.FileStorage.save"
        ).start()
        get_folders_mock = mock.patch("app.files.routes.get_folders").start()
        log_mock = mock.patch("app.files.routes.log").start()
        get_user_mock = mock.patch("app.files.routes.get_user").start()

        cfg_mock.CLOUD_PATH = Path("/cloud")
        get_folders_mock.return_value = folders
        get_user_mock.return_value = "user-foo"

        yield cfg_mock, file_storage_mock, get_folders_mock, log_mock, get_user_mock

        mock.patch.stopall()

    def test_one_file(self, client, upload_mocks):
        _, file_storage_mock, _, _, _ = upload_mocks

        rv = client.post(
            "/upload",
            data=dict(
                files=[(io.BytesIO(b"this is a test"), "test.pdf")],
                folder=0,
                submit="Upload",
            ),
            follow_redirects=True,
        )

        assert rv.status_code == 200
        file_storage_mock.assert_called_once_with("/cloud/folder-1/test.pdf")
        assert file_storage_mock.call_count == 1

        rv = client.post(
            "/upload",
            data=dict(
                files=[(io.BytesIO(b"this is a test"), "test.rar")],
                folder=2,
                submit="Upload",
            ),
            follow_redirects=True,
        )

        assert rv.status_code == 200
        file_storage_mock.assert_called_with("/cloud/folder-3/test.rar")
        assert file_storage_mock.call_count == 2

    def test_multiple_files(self, client, upload_mocks):
        _, file_storage_mock, _, _, _ = upload_mocks

        file_storage_mock.reset_mock()
        rv = client.post(
            "/upload",
            data=dict(
                files=[
                    (io.BytesIO(b"this is a test"), "test-1.py"),
                    (io.BytesIO(b"this is a test"), "test-2.py"),
                    (io.BytesIO(b"this is a test"), "test-3.py"),
                ],
                folder=2,
                submit="Upload",
            ),
            follow_redirects=True,
        )

        assert rv.status_code == 200
        file_storage_mock.assert_has_calls(
            [
                mock.call("/cloud/folder-3/test-1.py"),
                mock.call("/cloud/folder-3/test-2.py"),
                mock.call("/cloud/folder-3/test-3.py"),
            ]
        )

        assert file_storage_mock.call_count == 3

    def test_no_files(self, client, upload_mocks):
        _, file_storage_mock, _, _, _ = upload_mocks

        file_storage_mock.reset_mock()
        rv = client.post(
            "/upload",
            data=dict(files=[], folder=2, submit="Upload"),
            follow_redirects=True,
        )

        assert rv.status_code == 400
        assert b"No files supplied" in rv.data
        file_storage_mock.assert_not_called()

    def test_folder_as_str(self, client, upload_mocks):
        _, file_storage_mock, _, _, _ = upload_mocks

        rv = client.post(
            "/upload",
            data=dict(
                files=[(io.BytesIO(b"this is a test"), "whatever.rar")],
                folder="2",
                submit="Upload",
            ),
            follow_redirects=True,
        )

        assert rv.status_code == 200
        file_storage_mock.assert_called_once_with("/cloud/folder-3/whatever.rar")

    def test_no_folder(self, client, upload_mocks):
        _, file_storage_mock, _, _, _ = upload_mocks

        rv = client.post(
            "/upload",
            data=dict(
                files=[(io.BytesIO(b"this is a test"), "whatever.pdf")], submit="Upload"
            ),
            follow_redirects=True,
        )

        assert rv.status_code == 400
        assert b"No folder supplied" in rv.data
        file_storage_mock.assert_not_called()

    def test_type_invalid_folder(self, client, upload_mocks):
        _, file_storage_mock, _, _, _ = upload_mocks

        rv = client.post(
            "/upload",
            data=dict(
                files=[(io.BytesIO(b"this is a test"), "whatever.rar")],
                folder="-",
                submit="Upload",
            ),
            follow_redirects=True,
        )

        assert rv.status_code == 400
        assert b"No folder supplied or an invalid folder was supplied" in rv.data
        file_storage_mock.assert_not_called()

    def test_index_invalid_folder(self, client, upload_mocks):
        _, file_storage_mock, _, _, _ = upload_mocks

        rv = client.post(
            "/upload",
            data=dict(
                files=[(io.BytesIO(b"this is a test"), "whatever.rar")],
                folder=65,
                submit="Upload",
            ),
            follow_redirects=True,
        )

        assert rv.status_code == 400
        assert b"Invalid index folder" in rv.data
        file_storage_mock.assert_not_called()

    def test_methods(self, client, upload_mocks):
        rv = client.post("/upload")
        assert rv.status_code in [200, 400]

        assert client.get("/upload").status_code == 405
        assert client.put("/upload").status_code == 405
        assert client.delete("/upload").status_code == 405
        assert client.patch("/upload").status_code == 405


class TestDelete:
    @pytest.fixture(autouse=True)
    def delete_mocks(self):
        remove_mock = mock.patch("os.remove").start()
        cfg_mock = mock.patch("app.files.routes.cfg").start()
        rmtree_mock = mock.patch("shutil.rmtree").start()
        is_dir_mock = mock.patch("pathlib.Path.is_dir").start()
        get_user_mock = mock.patch("app.files.routes.get_user").start()
        log_mock = mock.patch("app.files.routes.log").start()

        cfg_mock.CLOUD_PATH = Path("/cloud")
        get_user_mock.return_value = "user-foo"

        yield remove_mock, cfg_mock, rmtree_mock, is_dir_mock, get_user_mock, log_mock

        mock.patch.stopall()

    @pytest.fixture(params=FILEPATHS)
    def filepath(self, request):
        return request.param

    def test_delete_file(self, delete_mocks, client, filepath):
        remove_mock, _, rmtree_mock, is_dir_mock, get_user_mock, log_mock = delete_mocks

        is_dir_mock.return_value = False

        url = f"/d/{filepath}/"
        delete_path = Path(f"/cloud/{filepath}")

        rv = client.get(url)
        assert rv.status_code == 200

        is_dir_mock.assert_called_once()
        remove_mock.assert_called_once_with(delete_path)
        rmtree_mock.assert_not_called()
        get_user_mock.assert_called_once_with()
        log_mock.assert_called_once_with(
            "User %r removed file %r", "user-foo", delete_path.as_posix()
        )

        assert b"File deleted" in rv.data
        assert delete_path.as_posix().encode() in rv.data

    def test_delete_folder(self, delete_mocks, client, filepath):
        remove_mock, _, rmtree_mock, is_dir_mock, get_user_mock, log_mock = delete_mocks
        is_dir_mock.return_value = True

        url = f"/d/{filepath}/"
        delete_path = Path(f"/cloud/{filepath}")

        rv = client.get(url)
        assert rv.status_code == 200

        is_dir_mock.assert_called_once()
        remove_mock.assert_not_called()
        rmtree_mock.assert_called_once_with(delete_path)
        get_user_mock.assert_called_once_with()
        log_mock.assert_called_once_with(
            "User %r removed tree %r", "user-foo", delete_path.as_posix()
        )

        assert b"Tree removed" in rv.data
        assert delete_path.as_posix().encode() in rv.data

    def test_delete_non_existing_file(self, delete_mocks, client, filepath):
        remove_mock, _, rmtree_mock, is_dir_mock, get_user_mock, log_mock = delete_mocks
        is_dir_mock.return_value = False
        remove_mock.side_effect = FileNotFoundError

        url = f"/d/{filepath}/"
        delete_path = Path(f"/cloud/{filepath}")

        rv = client.get(url)
        # assert rv.status_code == 404

        is_dir_mock.assert_called_once()
        remove_mock.assert_called_once_with(delete_path)
        rmtree_mock.assert_not_called()
        get_user_mock.assert_called_once_with()
        log_mock.assert_called_once_with(
            "User %r tried to incorrectly remove %r", "user-foo", delete_path.as_posix()
        )

        assert b"File not found" in rv.data
        assert delete_path.as_posix().encode() in rv.data

    def test_delete_non_existing_folder(self, delete_mocks, client, filepath):
        remove_mock, _, rmtree_mock, is_dir_mock, get_user_mock, log_mock = delete_mocks
        is_dir_mock.return_value = True
        rmtree_mock.side_effect = FileNotFoundError

        url = f"/d/{filepath}/"
        delete_path = Path(f"/cloud/{filepath}")

        rv = client.get(url)
        # assert rv.status_code == 404

        is_dir_mock.assert_called_once()
        remove_mock.assert_not_called()
        rmtree_mock.assert_called_once_with(delete_path)
        get_user_mock.assert_called_once_with()
        log_mock.assert_called_once_with(
            "User %r tried to incorrectly remove %r", "user-foo", delete_path.as_posix()
        )

        assert b"File not found" in rv.data
        assert delete_path.as_posix().encode() in rv.data


class TestMkdir:
    @pytest.fixture
    def mkdir_mocks(self):
        makedirs_mock = mock.patch("os.makedirs").start()
        cfg_mock = mock.patch("app.files.routes.cfg").start()
        log_mock = mock.patch("app.files.routes.log").start()
        get_user_mock = mock.patch("app.files.routes.get_user").start()

        cfg_mock.CLOUD_PATH = Path("/cloud")
        get_user_mock.return_value = "user-foo"

        yield makedirs_mock, cfg_mock, log_mock, get_user_mock
        mock.patch.stopall()

    @pytest.fixture(params=FILEPATHS)
    def filepath(self, request):
        return request.param

    def test_mkdir(self, client, mkdir_mocks, filepath):
        makedirs_mock, cfg_mock, log_mock, get_user_mock = mkdir_mocks

        url = f"/mkdir/{filepath}"
        client.get(url)

        make_path = Path(f"/cloud/{filepath}")

        makedirs_mock.assert_called_once_with(make_path)
        log_mock.assert_called_once_with("User %r made dir %r", "user-foo", filepath)
        get_user_mock.assert_called_once_with()


class TestMove:
    @pytest.fixture
    def move_mocks(self):
        log_mock = mock.patch("app.files.routes.log").start()
        get_user_mock = mock.patch(
            "app.files.routes.get_user", return_value="user-bar"
        ).start()
        move_mock = mock.patch("shutil.move").start()

        yield log_mock, get_user_mock, move_mock
        mock.patch.stopall()

    @pytest.mark.parametrize("_to", FILEPATHS)
    def test_without_from(self, move_mocks, client, _to):
        log_mock, get_user_mock, move_mock = move_mocks

        mv_url = f"/mv?to={_to}"
        rv = client.get(mv_url)
        assert rv.status_code == 400

        log_mock.assert_called_once_with(
            'User %r tried to move, but forgot "from" argument', "user-bar"
        )
        assert b'Missing "from" argument' in rv.data

    @pytest.mark.parametrize("_from", FILEPATHS)
    def test_without_to(self, move_mocks, client, _from):
        log_mock, get_user_mock, move_mock = move_mocks

        move_url = f"/mv?from={_from}"
        rv = client.get(move_url)
        assert rv.status_code == 400

        log_mock.assert_called_once_with(
            'User %r tried to move, but forgot "to" argument', "user-bar"
        )
        assert b'Missing "to" argument' in rv.data

    @pytest.mark.parametrize("_to, _from", product(FILEPATHS, FILEPATHS))
    def test_move_ok(self, move_mocks, client, _to, _from):
        log_mock, get_user_mock, move_mock = move_mocks

        move_url = f"/mv?from={_from}&to={_to}"
        rv = client.get(move_url)
        assert rv.status_code == 200

        log_mock.assert_called_once_with(
            "User %r moved file %r to %r", "user-bar", _from, _to
        )
        assert b"File moved correctly" in rv.data
