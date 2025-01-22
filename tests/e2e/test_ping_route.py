from ward import test, fixture, using

from tests.e2e.e2e_fixtures import client


@test("GET /ping", tags=["e2e", "ping"])
@using(client=client)
def _(client):
    # Act
    response = client.get("/ping")
    print(response)

    # Assert
    assert response.status_code == 200
    assert response.text == "pong"
