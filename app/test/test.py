from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


def test_route():
    response = client.get("/route")
    assert response.status_code == 200


def test_optimize():
    response = client.post("/route")
    assert response.status_code == 200
