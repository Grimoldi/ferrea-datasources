from ferrea.core.context import Context
from ferrea.models.datasource import BookDatasource
from pydantic import HttpUrl

from adapters.openlibrary import OpenLibraryRepository

ISBN = "0060930314"


def test_openlibrary_repository() -> None:
    """Test OpenLibrary service integration, happy path."""
    repository = OpenLibraryRepository(Context("tst", "tst"))
    data = repository.search_for_book_info(ISBN)

    if data is None:
        raise ValueError()

    expected_data = BookDatasource(
        title="Identity",
        authors=["Milan Kundera"],
        publishing="Harper Perennial",
        published_on=1999,
        cover=HttpUrl("https://covers.openlibrary.org/b/id/40647-M.jpg"),
        plot="A hotel in a small town on the Normandy coast, which they found in a guidebook.",
        languages=["eng"],
        book_formats=["edition"],
        authors_portrait=[
            HttpUrl("https://covers.openlibrary.org/a/olid/OL4326321A-M.jpg")
        ],
    )

    assert data == expected_data
