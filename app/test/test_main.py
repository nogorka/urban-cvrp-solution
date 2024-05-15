from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


# def test_optimize():
#     response = client.post("/route")
#     assert response.status_code == 200

def test_get_route_by_id():
    response = client.get("/route?id=663662ca9494b67cea8c85de")
    assert response.status_code == 200
    data = response.json()
    assert data["_id"] == "663662ca9494b67cea8c85de"
    assert len(data["route"]) > 0


def test_get_route_by_amount():
    response = client.get("/route?amount=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 10
