import pytest
from data_loader import ISBN, google_expected_data, openlibrary_expected_data
from fastapi.testclient import TestClient


@pytest.mark.skip(
    reason=(
        "Need to rethink about the main, since I'll have to patch the oas definition file, "
        "as its path exists only for the container."
        "And the patch/mock must be performed before the import of the app."
    )
)
def test_app() -> None:
    """Test app."""
    from app import app

    client = TestClient(app)

    response = client.get(f"/book/{ISBN}")

    expected_response_body = google_expected_data.update(openlibrary_expected_data())
    assert response.status_code == 200
    assert response.json() == expected_response_body
