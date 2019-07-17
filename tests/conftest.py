import pytest

from app import app


@pytest.fixture(scope='module')
def client():
    app.secret_key = 'asdfjewpoirjopfnñcxvkjs0i49309'
    testing_client = app.test_client()


    with app.app_context():
        yield testing_client
