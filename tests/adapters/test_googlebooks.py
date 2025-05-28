from ferrea.core.context import Context
from ferrea.models.datasource import BookDatasource
from pydantic import HttpUrl

from adapters.googlebooks import GoogleBooksRepository

# the cover seems to rotate on a pool of multiple links, unreliable as test
COVER_URL = HttpUrl(
    "https://books.google.com/books/content?id=mXPU2T--gPQC&printsec=frontcover&img=1&zoom=1&source=gbs_api"
)
PLOT = (
    "<p>There are situations in which we fail for a moment to recognize the person we are with, "
    "in which the identity of the other is erased while we simultaneously doubt our own. "
    'This also happens with couples--indeed, above all with couples, because lovers fear more than anything else "losing sight" of the loved one. '
    "<p>With stunning artfulness in expanding and playing variations on the meaningful moment, "
    "Milan Kundera has made this situation--and the vague sense of panic it inspires--the very fabric of his new novel. "
    "Here brevity goes hand in hand with intensity, and a moment of bewilderment marks the start of a labyrinthine journey "
    "during which the reader repeatedly crosses the border between the real and the unreal, between what occurs in the world "
    "outside and what the mind creates in its solitude. <p>Of all contemporary writers, only Kundera can transform such a hidden and "
    "disconcerting perception into the material for a novel, one of his finest, most painful, and most enlightening. "
    "Which, surprisingly, turns out to be a love story."
)
ISBN = "0060930314"


def test_googlebooks_repository() -> None:
    """Test Google Books service integration, happy path."""
    repository = GoogleBooksRepository(Context("tst", "tst"))
    data = repository.search_for_book_info(ISBN)

    if data is None:
        raise ValueError()

    data.cover = COVER_URL

    expected_data = BookDatasource(
        title="Identity",
        authors=["Milan Kundera"],
        publishing="HarperCollins",
        published_on=1999,
        cover=COVER_URL,
        plot=PLOT,
        languages=["en"],
        book_formats=["BOOK"],
    )

    assert data == expected_data
