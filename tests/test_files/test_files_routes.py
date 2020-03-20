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
    @pytest.fixture(scope="function", autouse=True)
    def mocks(self):
        folders = [Path(x) for x in ["folder-1", "folder-2", "folder-3"]]

        self.cfg_m = mock.patch("app.files.routes.cfg").start()
        self.save_m = mock.patch("werkzeug.datastructures.FileStorage.save").start()
        self.folders_m = mock.patch("app.files.routes.get_folders").start()
        self.log_m = mock.patch("app.files.routes.log").start()
        self.gu_m = mock.patch("app.files.routes.get_user").start()

        self.cfg_m.CLOUD_PATH = Path("/cloud")
        self.folders_m.return_value = folders
        self.gu_m.return_value = "user-foo"

        yield

        mock.patch.stopall()

    def test_one_file(self, client):
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
        self.folders_m.assert_called_once()

        self.log_m.assert_called()
        self.gu_m.assert_called()
        assert self.log_m.call_count == 2
        assert self.gu_m.call_count == 2

        self.save_m.assert_called_once_with("/cloud/folder-1/test.pdf")
        assert self.save_m.call_count == 1

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
        self.folders_m.assert_called()
        assert self.folders_m.call_count == 2

        self.log_m.assert_called()
        self.gu_m.assert_called()
        assert self.log_m.call_count == 4
        assert self.gu_m.call_count == 4

        self.save_m.assert_called_with("/cloud/folder-3/test.rar")
        assert self.save_m.call_count == 2

        assert b"success" in rv.data
        assert b"Files uploaded successfully" in rv.data

    def test_permission_error(self, client):
        exc = PermissionError("You can't save that here")
        self.save_m.side_effect = exc
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
        self.folders_m.assert_called_once()

        self.log_m.assert_called()
        self.gu_m.assert_called()
        assert self.log_m.call_count == 2
        assert self.gu_m.call_count == 2

        self.save_m.assert_called_once_with("/cloud/folder-1/test.pdf")
        assert self.save_m.call_count == 1

        assert b"Permission Error" in rv.data
        assert b"danger" in rv.data
        assert "PermissionError" in self.log_m.call_args_list[-1][0][0]

    def test_multiple_files(self, client):
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

        self.save_m.assert_any_call("/cloud/folder-3/test-1.py")
        self.save_m.assert_any_call("/cloud/folder-3/test-2.py")
        self.save_m.assert_any_call("/cloud/folder-3/test-3.py")
        assert self.save_m.call_count == 3

        self.folders_m.assert_called_once()
        self.log_m.assert_called()
        assert self.log_m.call_count == 2
        self.gu_m.assert_called()
        assert self.gu_m.call_count == 2

        assert b"success" in rv.data
        assert b"Files uploaded successfully" in rv.data

    def test_no_files(self, client):
        rv = client.post(
            "/upload",
            data={"files[]": [], "folder": 2, "submit": "Upload"},
            follow_redirects=True,
        )

        assert rv.status_code == 200
        assert b"No files supplied" in rv.data
        assert b"danger" in rv.data
        self.save_m.assert_not_called()

        self.folders_m.assert_called_once()
        self.log_m.assert_called_once()
        self.gu_m.assert_called_once()

    @pytest.mark.parametrize("nfiles", range(1, 4))
    def test_empty_file(self, client, nfiles):
        files = [(io.BytesIO(b""), "")] * nfiles
        rv = client.post(
            "/upload",
            data={"files[]": files, "folder": 2, "submit": "Upload",},
            follow_redirects=True,
        )

        assert rv.status_code == 200
        assert b"Supplied only %d empty files" % nfiles in rv.data
        assert b"danger" in rv.data
        self.save_m.assert_not_called()

        self.folders_m.assert_called_once()
        self.log_m.assert_called_once()
        self.gu_m.assert_called_once()

    def test_folder_as_str(self, client):
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
        self.save_m.assert_called_once_with("/cloud/folder-3/whatever.rar")
        self.folders_m.assert_called_once()

        self.log_m.assert_called()
        self.gu_m.assert_called()
        assert self.log_m.call_count == 2
        assert self.gu_m.call_count == 2

        assert b"success" in rv.data
        assert b"Files uploaded successfully" in rv.data

    def test_no_folder(self, client):
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
        assert b"danger" in rv.data
        self.save_m.assert_not_called()
        self.folders_m.assert_not_called()

        self.log_m.assert_called_once()
        self.gu_m.assert_called_once()

    def test_type_invalid_folder(self, client):
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
        assert b"danger" in rv.data
        self.save_m.assert_not_called()
        self.folders_m.assert_called_once()
        self.log_m.assert_called_once()
        self.gu_m.assert_called_once()

    def test_index_invalid_folder(self, client):
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
        assert b"danger" in rv.data
        self.save_m.assert_not_called()
        self.folders_m.assert_called_once()
        self.log_m.assert_called_once()
        self.gu_m.assert_called_once()

    def test_methods(self, client):
        assert client.post("/upload").status_code == 302
        assert client.post("/upload", follow_redirects=True).status_code == 200
        assert client.get("/upload").status_code == 405
        assert client.put("/upload").status_code == 405
        assert client.delete("/upload").status_code == 405
        assert client.patch("/upload").status_code == 405

        self.save_m.assert_not_called()
        self.folders_m.assert_not_called()
        self.log_m.assert_called()
        self.gu_m.assert_called()


class TestDelete:
    @pytest.fixture(scope="function", autouse=True)
    def mocks(self):
        self.rm_m = mock.patch("os.remove").start()
        self.cfg_m = mock.patch("app.files.routes.cfg").start()
        self.rmtree_m = mock.patch("shutil.rmtree").start()
        self.is_dir_m = mock.patch("pathlib.Path.is_dir").start()
        self.gu_m = mock.patch("app.files.routes.get_user").start()
        self.log_m = mock.patch("app.files.routes.log").start()

        self.cfg_m.CLOUD_PATH = Path("/cloud")
        self.gu_m.return_value = "user-foo"

        yield

        mock.patch.stopall()

    @pytest.fixture(params=FILEPATHS)
    def filepath(self, request):
        return request.param

    def test_delete_file(self, client, filepath):
        self.is_dir_m.return_value = False

        url = f"/d/{filepath}/"
        delete_path = Path(f"/cloud/{filepath}")

        rv = client.get(url)
        assert rv.status_code == 200

        self.is_dir_m.assert_called_once()
        self.rm_m.assert_called_once_with(delete_path)
        self.rmtree_m.assert_not_called()
        self.gu_m.assert_called_once_with()
        self.log_m.assert_called_once_with(
            "User %r removed file %r", "user-foo", delete_path.as_posix()
        )

        assert b"File deleted" in rv.data
        assert delete_path.as_posix().encode() in rv.data

    def test_delete_folder(self, client, filepath):
        self.is_dir_m.return_value = True

        url = f"/d/{filepath}/"
        delete_path = Path(f"/cloud/{filepath}")

        rv = client.get(url)
        assert rv.status_code == 200

        self.is_dir_m.assert_called_once()
        self.rm_m.assert_not_called()
        self.rmtree_m.assert_called_once_with(delete_path)
        self.gu_m.assert_called_once_with()
        self.log_m.assert_called_once_with(
            "User %r removed tree %r", "user-foo", delete_path.as_posix()
        )

        assert b"Tree removed" in rv.data
        assert delete_path.as_posix().encode() in rv.data

    def test_delete_non_existing_file(self, client, filepath):
        self.is_dir_m.return_value = False
        self.rm_m.side_effect = FileNotFoundError

        url = f"/d/{filepath}/"
        delete_path = Path(f"/cloud/{filepath}")

        rv = client.get(url)
        # assert rv.status_code == 404

        self.is_dir_m.assert_called_once()
        self.rm_m.assert_called_once_with(delete_path)
        self.rmtree_m.assert_not_called()
        self.gu_m.assert_called_once_with()
        self.log_m.assert_called_once_with(
            "User %r tried to incorrectly remove %r", "user-foo", delete_path.as_posix()
        )

        assert b"File not found" in rv.data
        assert delete_path.as_posix().encode() in rv.data

    def test_delete_non_existing_folder(self, client, filepath):
        self.is_dir_m.return_value = True
        self.rmtree_m.side_effect = FileNotFoundError

        url = f"/d/{filepath}/"
        delete_path = Path(f"/cloud/{filepath}")

        rv = client.get(url)

        self.is_dir_m.assert_called_once()
        self.rm_m.assert_not_called()
        self.rmtree_m.assert_called_once_with(delete_path)
        self.gu_m.assert_called_once_with()
        self.log_m.assert_called_once_with(
            "User %r tried to incorrectly remove %r", "user-foo", delete_path.as_posix()
        )

        assert b"File not found" in rv.data
        assert delete_path.as_posix().encode() in rv.data


class TestMkdir:
    @pytest.fixture(scope="function", autouse=True)
    def mocks(self):
        self.mkdirs_m = mock.patch("os.makedirs").start()
        self.cfg_m = mock.patch("app.files.routes.cfg").start()
        self.log_m = mock.patch("app.files.routes.log").start()
        self.gu_m = mock.patch("app.files.routes.get_user").start()

        self.cfg_m.CLOUD_PATH = Path("/cloud")
        self.gu_m.return_value = "user-foo"

        yield
        mock.patch.stopall()

    @pytest.fixture(params=FILEPATHS)
    def filepath(self, request):
        return request.param

    def test_mkdir(self, client, filepath):
        url = f"/mkdir/{filepath}"
        client.get(url)

        make_path = Path(f"/cloud/{filepath}")

        self.mkdirs_m.assert_called_once_with(make_path)
        self.log_m.assert_called_once_with("User %r made dir %r", "user-foo", filepath)
        self.gu_m.assert_called_once_with()


class TestMove:
    @pytest.fixture(scope="function", autouse=True)
    def mocks(self):
        self.log_m = mock.patch("app.files.routes.log").start()
        self.gu_m = mock.patch(
            "app.files.routes.get_user", return_value="user-bar"
        ).start()
        self.mv_m = mock.patch("shutil.move").start()

        yield
        mock.patch.stopall()

    @pytest.mark.parametrize("_to", FILEPATHS)
    def test_without_from(self, client, _to):
        mv_url = f"/mv?to={_to}"
        rv = client.get(mv_url)
        assert rv.status_code == 400

        self.log_m.assert_called_once_with(
            'User %r tried to move, but forgot "from" argument', "user-bar"
        )
        self.gu_m.assert_called_once()
        self.mv_m.assert_not_called()
        assert b'Missing "from" argument' in rv.data

    @pytest.mark.parametrize("_from", FILEPATHS)
    def test_without_to(self, client, _from):
        move_url = f"/mv?from={_from}"
        rv = client.get(move_url)
        assert rv.status_code == 400

        self.log_m.assert_called_once_with(
            'User %r tried to move, but forgot "to" argument', "user-bar"
        )
        self.gu_m.assert_called_once()
        self.mv_m.assert_not_called()
        assert b'Missing "to" argument' in rv.data

    @pytest.mark.parametrize("_to, _from", product(FILEPATHS, FILEPATHS))
    def test_move_ok(self, client, _to, _from):
        move_url = f"/mv?from={_from}&to={_to}"
        rv = client.get(move_url)
        assert rv.status_code == 200

        self.log_m.assert_called_once_with(
            "User %r moved file %r to %r", "user-bar", _from, _to
        )
        self.gu_m.assert_called_once()
        self.mv_m.assert_called_once()
        assert b"File moved correctly" in rv.data

    @pytest.mark.parametrize("exc", [FileNotFoundError, FileExistsError])
    @pytest.mark.parametrize("_to, _from", product(FILEPATHS, FILEPATHS))
    def test_move_error(self, client, _to, _from, exc):
        self.mv_m.side_effect = exc
        move_url = f"/mv?from={_from}&to={_to}"
        rv = client.get(move_url)
        assert rv.status_code == 400

        self.log_m.assert_called_once()
        self.gu_m.assert_called_once()
        assert b"File not found" in rv.data
