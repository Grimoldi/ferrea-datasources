from data_loader import ISBN, google_expected_data

from models.api_google import GoogleBooksAPI
from operations.service_google import GoogleBooksService

GOOGLE_API = "https://www.googleapis.com/books/v1"


def test_google_service() -> None:
    """Test Google service integration, happy path."""
    gb_api = GoogleBooksAPI(GOOGLE_API)
    gb_service = GoogleBooksService(gb_api)
    book_data = gb_service.get_book_data(ISBN)

    if book_data is None:
        raise ValueError()

    data = book_data.serialize()
    # the cover seems to rotate on a pool of multiple links, unreliable as test
    data["cover"] = ""

    expected_data = google_expected_data()

    assert data == expected_data


def test_google_service_not_found() -> None:
    """Test Google service integration, book not found."""
    DEFINITELY_NOT_AN_ISBN = "404"

    gb_api = GoogleBooksAPI(GOOGLE_API)
    gb_service = GoogleBooksService(gb_api)
    book_data = gb_service.get_book_data(DEFINITELY_NOT_AN_ISBN)

    assert book_data is None
