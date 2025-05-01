import json
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

ISBN = "0060930314"
TEST_DATA_FOLDER = "test_data"
GOOGLE_BOOKS_FILEDATA = "google_books.json"
OPENLIBRARY_FILEDATA = "openlibrary.json"


def _load_test_data(filename: str) -> dict[str, Any]:
    """Loads a data file located under tests/test_data folder."""
    data_file = Path(__file__).parent / TEST_DATA_FOLDER / filename
    return json.loads(str(data_file))


def _google_data() -> dict[str, Any]:
    """Google books tests data."""
    return _load_test_data(GOOGLE_BOOKS_FILEDATA)


def _openlibrary_expected_data() -> dict[str, Any]:
    """OpenLibrary tests data."""
    # # "author_portreait": "https://covers.openlibrary.org/a/id/6677922-M.jpg"
    return _load_test_data(OPENLIBRARY_FILEDATA)


@pytest.mark.skip(
    reason=(
        "Need to rethink about the main, since I'll have to patch the oas definition file, "
        "since it's loaded only in the container."
        "And the patch/mock must be performed before the import of the app."
    )
)
def test_app() -> None:
    """Test app."""
    from app import app

    client = TestClient(app)

    response = client.get(f"/book/{ISBN}")

    expected_response_body = _google_data.update(_openlibrary_expected_data())
    assert response.status_code == 200
    assert response.json() == expected_response_body
