def test_index(client):
    rs = client.get('/')

    assert rs.status_code == 200
    assert b"Alloza's Cloud" in rs.data
    assert b'folder' in rs.data
    assert b'Files' in rs.data
    assert b'Upload' in rs.data

    assert client.post('/').status_code == 405
    assert client.patch('/').status_code == 405
    assert client.delete('/').status_code == 405
    assert client.put('/').status_code == 405
