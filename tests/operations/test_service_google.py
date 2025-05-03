import pprint

from data_loader import ISBN, google_data

from models.api_google import GoogleBooksAPI
from operations.service_google import GoogleBooksService


def test_google_service() -> None:
    """Test Google service integration."""
    gb_api = GoogleBooksAPI("https://www.googleapis.com/books/v1")
    gb_service = GoogleBooksService(gb_api)
    book_data = gb_service.get_book_data(ISBN)

    if book_data is None:
        raise ValueError()

    data = book_data.serialize()
    # the cover seems to rotate on a pool of multiple links, unreliable as test
    data["cover"] = ""

    expected_data = google_data()

    assert data == expected_data
