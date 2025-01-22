from ward import fixture

from main import app


@fixture
def client():
    with app.test_client() as client:
        yield client
