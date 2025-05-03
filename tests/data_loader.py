import json
from pathlib import Path
from typing import Any

TEST_DATA_FOLDER = "test_data"
GOOGLE_BOOKS_FILEDATA = "google_books.json"
OPENLIBRARY_FILEDATA = "openlibrary.json"
ISBN = "0060930314"


def _load_test_data(filename: str) -> dict[str, Any]:
    """Loads a data file located under tests/test_data folder."""
    data_file = Path(__file__).parent / TEST_DATA_FOLDER / filename
    with open(data_file, "r") as f:
        data = json.loads(f.read())

    return data


def google_data() -> dict[str, Any]:
    """Google books tests data."""
    return _load_test_data(GOOGLE_BOOKS_FILEDATA)


def openlibrary_expected_data() -> dict[str, Any]:
    """OpenLibrary tests data."""
    # # "author_portreait": "https://covers.openlibrary.org/a/id/6677922-M.jpg"
    return _load_test_data(OPENLIBRARY_FILEDATA)
