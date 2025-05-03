from data_loader import ISBN, openlibrary_expected_data

from models.api_openlibrary import OpenLibraryAPI
from operations.service_openlibrary import OpenLibraryService

OPENLIBRARY_API = "http://openlibrary.org/api/books"


def test_openlibrary_service() -> None:
    """Test GooOpenLibrary service integration, happy path."""
    ol_api = OpenLibraryAPI(OPENLIBRARY_API)
    ol_service = OpenLibraryService(ol_api)
    data = ol_service.get_author_portrait(ISBN)

    if data is None:
        raise ValueError()

    print(data)

    assert data == openlibrary_expected_data()


def test_openlibrary_service_not_found() -> None:
    """Test GooOpenLibrary service integration, author not found."""
    DEFINITELY_NOT_AN_ISBN = "404"

    ol_api = OpenLibraryAPI(OPENLIBRARY_API)
    ol_service = OpenLibraryService(ol_api)
    data = ol_service.get_author_portrait(DEFINITELY_NOT_AN_ISBN)

    assert data is None
