import pytest

from app import create_app


@pytest.fixture(scope="session", autouse=True)
def app():
    application = create_app()
    yield application


@pytest.fixture(scope="module")
def client(app):
    app.secret_key = "secret-known"
    testing_client = app.test_client()

    with app.app_context():
        yield testing_client
