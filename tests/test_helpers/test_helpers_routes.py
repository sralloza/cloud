from unittest import mock


@mock.patch("app.helpers.routes.add_to_ignored")
def test_ignore(add_ignored_mock, client):
    rv = client.get("/ignore/path/to/folder")

    add_ignored_mock.assert_called_once_with("path/to/folder")
    assert rv.status_code == 200


@mock.patch("app.helpers.routes.get_ignored")
def test_show_ignored(get_ignored_mock, client):
    get_ignored_mock.return_value = ["a", "b", "c", "d"]
    rv = client.get("/show-ignored")

    get_ignored_mock.assert_called_once()
    assert rv.status_code == 200
    assert rv.data == b"a<br>b<br>c<br>d"


@mock.patch("app.helpers.routes.remove_from_ignored")
def test_unignore(remove_ignored_mock, client):
    rv = client.get("/unignore/path/to/folder")

    remove_ignored_mock.assert_called_once_with("path/to/folder")
    assert rv.status_code == 200


@mock.patch("app.helpers.routes.get_ignored")
@mock.patch("app.helpers.routes.remove_from_ignored")
def test_unignore_all(remove_ignored_mock, get_ignored_mock, client):
    get_ignored_mock.return_value = ["folder-1", "folder-2", "folder-3"]
    rv = client.get("/unignore-all")

    remove_ignored_mock.assert_called()
    remove_ignored_mock.assert_any_call("folder-1")
    remove_ignored_mock.assert_any_call("folder-2")
    remove_ignored_mock.assert_any_call("folder-3")
    assert remove_ignored_mock.call_count == 3

    get_ignored_mock.assert_called_once()
