 from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == (
        "Hello World from SEGES Data Science {{ cookiecutter.long_name }} endpoint. BUILD_NUMBER = 'test_build_number'."
    )


def test_secure():
    credentials = HTTPBasicAuth(username="my_username", password="my_password")
    response = client.get(
        "/secure",
        headers={"WWW-Authenticate": "Basic"},
        auth=credentials,
    )
    assert response.status_code == 200


def test_bad_auth_fails():
    credentials = HTTPBasicAuth(username="wrong_username", password="wrong_username")
    response = client.get(
        "/secure",
        headers={"WWW-Authenticate": "Basic"},
        auth=credentials,
    )
    assert response.status_code == 401, response.text
    assert response.json() == {"detail": "Incorrect username or password"}