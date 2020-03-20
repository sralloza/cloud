from unittest import mock


@mock.patch("app.helpers.routes.add_to_ignored")
def test_ignore(add_ign_m, client):
    rv = client.get("/ignore/path/to/folder")

    add_ign_m.assert_called_once_with("path/to/folder")
    assert rv.status_code == 200


@mock.patch("app.helpers.routes.get_ignored")
def test_show_ignored(get_ign_m, client):
    get_ign_m.return_value = ["a", "b", "c", "d"]
    rv = client.get("/show-ignored")

    get_ign_m.assert_called_once()
    assert rv.status_code == 200
    assert rv.data == b"a<br>b<br>c<br>d"


@mock.patch("app.helpers.routes.remove_from_ignored")
def test_unignore(rem_igm_m, client):
    rv = client.get("/unignore/path/to/folder")

    rem_igm_m.assert_called_once_with("path/to/folder")
    assert rv.status_code == 200


@mock.patch("app.helpers.routes.get_ignored")
@mock.patch("app.helpers.routes.remove_from_ignored")
def test_unignore_all(rem_igm_m, get_ign_m, client):
    get_ign_m.return_value = ["folder-1", "folder-2", "folder-3"]
    rv = client.get("/unignore-all")

    rem_igm_m.assert_called()
    rem_igm_m.assert_any_call("folder-1")
    rem_igm_m.assert_any_call("folder-2")
    rem_igm_m.assert_any_call("folder-3")
    assert rem_igm_m.call_count == 3

    get_ign_m.assert_called_once()
