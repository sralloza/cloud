from unittest import mock


@mock.patch("app.helpers.routes.add_to_hides")
def test_hide(add_hides_mock, client):
    rv = client.get("/hide/path/to/folder")

    add_hides_mock.assert_called_once_with("path/to/folder")
    assert rv.status_code == 200


@mock.patch("app.helpers.routes.get_hides")
def test_show_hides(get_hides_mock, client):
    get_hides_mock.return_value = ["a", "b", "c", "d"]
    rv = client.get("/show-hides")

    get_hides_mock.assert_called_once()
    assert rv.status_code == 200
    assert rv.data == b"a<br>b<br>c<br>d"


@mock.patch("app.helpers.routes.remove_from_hides")
def test_unhide(remove_hide_mock, client):
    rv = client.get("/unhide/path/to/folder")

    remove_hide_mock.assert_called_once_with("path/to/folder")
    assert rv.status_code == 200


@mock.patch("app.helpers.routes.get_hides")
@mock.patch("app.helpers.routes.remove_from_hides")
def test_unhide_all(remove_hides_mock, get_hides_mock, client):
    get_hides_mock.return_value = ["folder-1", "folder-2", "folder-3"]
    rv = client.get("/unhide-all")

    remove_hides_mock.assert_called()
    remove_hides_mock.assert_any_call("folder-1")
    remove_hides_mock.assert_any_call("folder-2")
    remove_hides_mock.assert_any_call("folder-3")
    assert remove_hides_mock.call_count == 3

    get_hides_mock.assert_called_once()
