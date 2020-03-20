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
        save_mock = mock.patch("werkzeug.datastructures.FileStorage.save").start()
        folders_mock = mock.patch("app.files.routes.get_folders").start()
        log_mock = mock.patch("app.files.routes.log").start()
        gu_mock = mock.patch("app.files.routes.get_user").start()

        cfg_mock.CLOUD_PATH = Path("/cloud")
        folders_mock.return_value = folders
        gu_mock.return_value = "user-foo"

        yield save_mock, folders_mock, log_mock, gu_mock

        mock.patch.stopall()

    def test_one_file(self, client, upload_mocks):
        save_mock, folders_mock, log_mock, gu_mock = upload_mocks

        rv = client.post(
            "/upload",
            data={
                "files[]": [(io.BytesIO(b"this is a test"), "test.pdf")],
                "folder": 0,
                "submit": "Upload",
            },
            follow_redirects=True,
        )

        assert rv.status_code == 200
        folders_mock.assert_called_once()

        log_mock.assert_called()
        gu_mock.assert_called()
        assert log_mock.call_count == 2
        assert gu_mock.call_count == 2

        save_mock.assert_called_once_with("/cloud/folder-1/test.pdf")
        assert save_mock.call_count == 1

        rv = client.post(
            "/upload",
            data={
                "files[]": [(io.BytesIO(b"this is a test"), "test.rar")],
                "folder": 2,
                "submit": "Upload",
            },
            follow_redirects=True,
        )

        assert rv.status_code == 200
        folders_mock.assert_called()
        assert folders_mock.call_count == 2

        log_mock.assert_called()
        gu_mock.assert_called()
        assert log_mock.call_count == 4
        assert gu_mock.call_count == 4

        save_mock.assert_called_with("/cloud/folder-3/test.rar")
        assert save_mock.call_count == 2

    def test_permission_error(self, client, upload_mocks):
        save_mock, folders_mock, log_mock, gu_mock = upload_mocks


        exc = PermissionError("You can't save that here")
        save_mock.side_effect = exc
        rv = client.post(
            "/upload",
            data={
                "files[]": [(io.BytesIO(b"this is a test"), "test.pdf")],
                "folder": 0,
                "submit": "Upload",
            },
            follow_redirects=True,
        )

        assert rv.status_code == 200
        folders_mock.assert_called_once()

        log_mock.assert_called()
        gu_mock.assert_called()
        assert log_mock.call_count == 2
        assert gu_mock.call_count == 2

        save_mock.assert_called_once_with("/cloud/folder-1/test.pdf")
        assert save_mock.call_count == 1

        assert b"Permission Error" in rv.data
        assert "PermissionError" in log_mock.call_args_list[-1][0][0]

    def test_multiple_files(self, client, upload_mocks):
        save_mock, folders_mock, log_mock, gu_mock = upload_mocks

        rv = client.post(
            "/upload",
            data={
                "files[]": [
                    (io.BytesIO(b"this is a test"), "test-1.py"),
                    (io.BytesIO(b"this is a test"), "test-2.py"),
                    (io.BytesIO(b"this is a test"), "test-3.py"),
                ],
                "folder": 2,
                "submit": "Upload",
            },
            follow_redirects=True,
        )

        assert rv.status_code == 200

        save_mock.assert_any_call("/cloud/folder-3/test-1.py")
        save_mock.assert_any_call("/cloud/folder-3/test-2.py")
        save_mock.assert_any_call("/cloud/folder-3/test-3.py")
        assert save_mock.call_count == 3

        folders_mock.assert_called_once()
        log_mock.assert_called()
        assert log_mock.call_count == 2
        gu_mock.assert_called()
        assert gu_mock.call_count == 2

    def test_no_files(self, client, upload_mocks):
        save_mock, folders_mock, log_mock, gu_mock = upload_mocks

        rv = client.post(
            "/upload",
            data={"files[]": [], "folder": 2, "submit": "Upload"},
            follow_redirects=True,
        )

        assert rv.status_code == 200
        assert b"No files supplied" in rv.data
        save_mock.assert_not_called()

        folders_mock.assert_called_once()
        log_mock.assert_called_once()
        gu_mock.assert_called_once()

    @pytest.mark.parametrize("nfiles", range(1, 4))
    def test_empty_file(self, client, upload_mocks, nfiles):
        save_mock, folders_mock, log_mock, gu_mock = upload_mocks

        files = [(io.BytesIO(b""), "")] * nfiles
        rv = client.post(
            "/upload",
            data={"files[]": files, "folder": 2, "submit": "Upload",},
            follow_redirects=True,
        )

        assert rv.status_code == 200
        assert b"Supplied only %d empty files" % nfiles in rv.data
        save_mock.assert_not_called()

        folders_mock.assert_called_once()
        log_mock.assert_called_once()
        gu_mock.assert_called_once()

    def test_folder_as_str(self, client, upload_mocks):
        save_mock, folders_mock, log_mock, gu_mock = upload_mocks

        rv = client.post(
            "/upload",
            data={
                "files[]": [(io.BytesIO(b"this is a test"), "whatever.rar")],
                "folder": "2",
                "submit": "Upload",
            },
            follow_redirects=True,
        )

        assert rv.status_code == 200
        save_mock.assert_called_once_with("/cloud/folder-3/whatever.rar")
        folders_mock.assert_called_once()

        log_mock.assert_called()
        gu_mock.assert_called()
        assert log_mock.call_count == 2
        assert gu_mock.call_count == 2

    def test_no_folder(self, client, upload_mocks):
        save_mock, folders_mock, log_mock, gu_mock = upload_mocks

        rv = client.post(
            "/upload",
            data={
                "files[]": [(io.BytesIO(b"this is a test"), "whatever.pdf")],
                "submit": "Upload",
            },
            follow_redirects=True,
        )

        assert rv.status_code == 200
        assert b"No folder supplied" in rv.data
        save_mock.assert_not_called()
        folders_mock.assert_not_called()

        log_mock.assert_called_once()
        gu_mock.assert_called_once()

    def test_type_invalid_folder(self, client, upload_mocks):
        save_mock, folders_mock, log_mock, gu_mock = upload_mocks

        rv = client.post(
            "/upload",
            data={
                "files[]": [(io.BytesIO(b"this is a test"), "whatever.rar")],
                "folder": "-",
                "submit": "Upload",
            },
            follow_redirects=True,
        )

        assert rv.status_code == 200
        assert b"Invalid index folder" in rv.data
        save_mock.assert_not_called()
        folders_mock.assert_called_once()
        log_mock.assert_called_once()
        gu_mock.assert_called_once()

    def test_index_invalid_folder(self, client, upload_mocks):
        save_mock, folders_mock, log_mock, gu_mock = upload_mocks

        rv = client.post(
            "/upload",
            data={
                "files[]": [(io.BytesIO(b"this is a test"), "whatever.rar")],
                "folder": 99999999999,
                "submit": "Upload",
            },
            follow_redirects=True,
        )

        assert rv.status_code == 200
        assert b"Invalid index folder" in rv.data
        save_mock.assert_not_called()
        folders_mock.assert_called_once()
        log_mock.assert_called_once()
        gu_mock.assert_called_once()

    def test_methods(self, client, upload_mocks):
        save_mock, folders_mock, log_mock, gu_mock = upload_mocks

        assert client.post("/upload").status_code == 302
        assert client.post("/upload", follow_redirects=True).status_code == 200
        assert client.get("/upload").status_code == 405
        assert client.put("/upload").status_code == 405
        assert client.delete("/upload").status_code == 405
        assert client.patch("/upload").status_code == 405

        save_mock.assert_not_called()
        folders_mock.assert_not_called()
        log_mock.assert_called()
        gu_mock.assert_called()


class TestDelete:
    @pytest.fixture(autouse=True)
    def delete_mocks(self):
        remove_mock = mock.patch("os.remove").start()
        cfg_mock = mock.patch("app.files.routes.cfg").start()
        rmtree_mock = mock.patch("shutil.rmtree").start()
        is_dir_mock = mock.patch("pathlib.Path.is_dir").start()
        gu_mock = mock.patch("app.files.routes.get_user").start()
        log_mock = mock.patch("app.files.routes.log").start()

        cfg_mock.CLOUD_PATH = Path("/cloud")
        gu_mock.return_value = "user-foo"

        yield remove_mock, cfg_mock, rmtree_mock, is_dir_mock, gu_mock, log_mock

        mock.patch.stopall()

    @pytest.fixture(params=FILEPATHS)
    def filepath(self, request):
        return request.param

    def test_delete_file(self, delete_mocks, client, filepath):
        remove_mock, _, rmtree_mock, is_dir_mock, gu_mock, log_mock = delete_mocks

        is_dir_mock.return_value = False

        url = f"/d/{filepath}/"
        delete_path = Path(f"/cloud/{filepath}")

        rv = client.get(url)
        assert rv.status_code == 200

        is_dir_mock.assert_called_once()
        remove_mock.assert_called_once_with(delete_path)
        rmtree_mock.assert_not_called()
        gu_mock.assert_called_once_with()
        log_mock.assert_called_once_with(
            "User %r removed file %r", "user-foo", delete_path.as_posix()
        )

        assert b"File deleted" in rv.data
        assert delete_path.as_posix().encode() in rv.data

    def test_delete_folder(self, delete_mocks, client, filepath):
        remove_mock, _, rmtree_mock, is_dir_mock, gu_mock, log_mock = delete_mocks
        is_dir_mock.return_value = True

        url = f"/d/{filepath}/"
        delete_path = Path(f"/cloud/{filepath}")

        rv = client.get(url)
        assert rv.status_code == 200

        is_dir_mock.assert_called_once()
        remove_mock.assert_not_called()
        rmtree_mock.assert_called_once_with(delete_path)
        gu_mock.assert_called_once_with()
        log_mock.assert_called_once_with(
            "User %r removed tree %r", "user-foo", delete_path.as_posix()
        )

        assert b"Tree removed" in rv.data
        assert delete_path.as_posix().encode() in rv.data

    def test_delete_non_existing_file(self, delete_mocks, client, filepath):
        remove_mock, _, rmtree_mock, is_dir_mock, gu_mock, log_mock = delete_mocks
        is_dir_mock.return_value = False
        remove_mock.side_effect = FileNotFoundError

        url = f"/d/{filepath}/"
        delete_path = Path(f"/cloud/{filepath}")

        rv = client.get(url)
        # assert rv.status_code == 404

        is_dir_mock.assert_called_once()
        remove_mock.assert_called_once_with(delete_path)
        rmtree_mock.assert_not_called()
        gu_mock.assert_called_once_with()
        log_mock.assert_called_once_with(
            "User %r tried to incorrectly remove %r", "user-foo", delete_path.as_posix()
        )

        assert b"File not found" in rv.data
        assert delete_path.as_posix().encode() in rv.data

    def test_delete_non_existing_folder(self, delete_mocks, client, filepath):
        remove_mock, _, rmtree_mock, is_dir_mock, gu_mock, log_mock = delete_mocks
        is_dir_mock.return_value = True
        rmtree_mock.side_effect = FileNotFoundError

        url = f"/d/{filepath}/"
        delete_path = Path(f"/cloud/{filepath}")

        rv = client.get(url)
        # assert rv.status_code == 404

        is_dir_mock.assert_called_once()
        remove_mock.assert_not_called()
        rmtree_mock.assert_called_once_with(delete_path)
        gu_mock.assert_called_once_with()
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
        gu_mock = mock.patch("app.files.routes.get_user").start()

        cfg_mock.CLOUD_PATH = Path("/cloud")
        gu_mock.return_value = "user-foo"

        yield makedirs_mock, cfg_mock, log_mock, gu_mock
        mock.patch.stopall()

    @pytest.fixture(params=FILEPATHS)
    def filepath(self, request):
        return request.param

    def test_mkdir(self, client, mkdir_mocks, filepath):
        makedirs_mock, cfg_mock, log_mock, gu_mock = mkdir_mocks

        url = f"/mkdir/{filepath}"
        client.get(url)

        make_path = Path(f"/cloud/{filepath}")

        makedirs_mock.assert_called_once_with(make_path)
        log_mock.assert_called_once_with("User %r made dir %r", "user-foo", filepath)
        gu_mock.assert_called_once_with()


class TestMove:
    @pytest.fixture
    def move_mocks(self):
        log_mock = mock.patch("app.files.routes.log").start()
        gu_mock = mock.patch(
            "app.files.routes.get_user", return_value="user-bar"
        ).start()
        move_mock = mock.patch("shutil.move").start()

        yield log_mock, gu_mock, move_mock
        mock.patch.stopall()

    @pytest.mark.parametrize("_to", FILEPATHS)
    def test_without_from(self, move_mocks, client, _to):
        log_mock, gu_mock, move_mock = move_mocks

        mv_url = f"/mv?to={_to}"
        rv = client.get(mv_url)
        assert rv.status_code == 400

        log_mock.assert_called_once_with(
            'User %r tried to move, but forgot "from" argument', "user-bar"
        )
        gu_mock.assert_called_once()
        move_mock.assert_not_called()
        assert b'Missing "from" argument' in rv.data

    @pytest.mark.parametrize("_from", FILEPATHS)
    def test_without_to(self, move_mocks, client, _from):
        log_mock, gu_mock, move_mock = move_mocks

        move_url = f"/mv?from={_from}"
        rv = client.get(move_url)
        assert rv.status_code == 400

        log_mock.assert_called_once_with(
            'User %r tried to move, but forgot "to" argument', "user-bar"
        )
        gu_mock.assert_called_once()
        move_mock.assert_not_called()
        assert b'Missing "to" argument' in rv.data

    @pytest.mark.parametrize("_to, _from", product(FILEPATHS, FILEPATHS))
    def test_move_ok(self, move_mocks, client, _to, _from):
        log_mock, gu_mock, move_mock = move_mocks

        move_url = f"/mv?from={_from}&to={_to}"
        rv = client.get(move_url)
        assert rv.status_code == 200

        log_mock.assert_called_once_with(
            "User %r moved file %r to %r", "user-bar", _from, _to
        )
        gu_mock.assert_called_once()
        move_mock.assert_called_once()
        assert b"File moved correctly" in rv.data

    @pytest.mark.parametrize("exc", [FileNotFoundError, FileExistsError])
    @pytest.mark.parametrize("_to, _from", product(FILEPATHS, FILEPATHS))
    def test_move_error(self, move_mocks, client, _to, _from, exc):
        log_mock, gu_mock, move_mock = move_mocks
        move_mock.side_effect = exc

        move_url = f"/mv?from={_from}&to={_to}"
        rv = client.get(move_url)
        assert rv.status_code == 400

        log_mock.assert_called_once()
        gu_mock.assert_called_once()
        assert b"File not found" in rv.data
