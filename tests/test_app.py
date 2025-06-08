from fastapi.testclient import TestClient

from app import app

ISBN = "0060930314"


def test_app_happy_path() -> None:
    """Test app when everything goes as expected."""

    client = TestClient(app())

    response = client.get(f"/book/{ISBN}")

    assert response.status_code == 200


def test_app_not_found() -> None:
    """Test with a not existing isbn."""

    client = TestClient(app())

    response = client.get("/book/123456789")

    assert response.status_code == 404
