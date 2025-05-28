import pytest
from fastapi.testclient import TestClient

ISBN = "0060930314"


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

    assert response.status_code == 200
