import re
from dataclasses import dataclass
from typing import Any

import httpx
import jmespath
from ferrea.core.context import Context
from ferrea.models.datasource import BookDatasource
from ferrea.observability.logs import ferrea_logger
from pydantic import HttpUrl

from configs import settings

GOOGLE_API_BASE_URL = settings.google.api_url

BOOK_DATA = "book"
AUTHOR_DATA = "author"
PORTRAIT_DATA = "cover"


@dataclass
class GoogleBooksRepository:
    """
    Google Books Repository for query towards Google API Service.

    Please note that Google states that the result could be depending upon the localization.
    For further reading, refer to: https://developers.google.com/books/docs/v1/using#UserLocation


    Refer to https://developers.google.com/books/docs/overview for documentation.
    """

    context: Context

    def search_for_book_info(self, isbn: str) -> BookDatasource | None:
        """Search on Google Books the required isbn for book information.

        Args:
            isbn (str): the isbn of the book.

        Returns:
            BookDatasource | None: the instance with the fetched information or None if not found.
        """
        book_summary = self._perform_isbn_search(isbn)
        if book_summary is None:
            return None

        book_id = book_summary["items"][0]["id"]
        self._datasource = self._perform_book_fetch(book_id)

        return self._deserialize_data()

    def _perform_isbn_search(self, isbn: str) -> dict[str, Any] | None:
        """Perform a search on Google Books to see if the isbn is known.

        Args:
            isbn (str): the isbn of the book.

        Returns:
            dict[str, Any] | None: the response from the service or None if book not found.
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        qp = {
            "q": f"isbn:{isbn}",
            "projection": "lite",
        }
        uri = f"{GOOGLE_API_BASE_URL}/volumes"

        with httpx.Client() as client:
            response = client.get(
                uri,
                headers=headers,
                params=qp,
                follow_redirects=True,
            )

        if response.json()["totalItems"] == 0:
            ferrea_logger.info(
                (
                    f"Unable to find {isbn} on Google Books."
                    f" Response is {response.status_code} {response}"
                ),
                **self.context.log,
            )
            return None
        return response.json()

    def _perform_book_fetch(self, book_id: str) -> dict[str, Any] | None:
        """Given a book id, fetch the single resource.

        Args:
            book_id (str): the Google Books ID.

        Returns:
            dict[str, Any] | None: the response from the service or None if book not found.
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        uri = f"{GOOGLE_API_BASE_URL}/volumes/{book_id}"

        with httpx.Client() as client:
            response = client.get(
                uri,
                headers=headers,
                follow_redirects=True,
            )

        if not response.status_code == httpx.codes.OK:
            ferrea_logger.info(
                (
                    f"Unable to find {book_id} on Google Books."
                    f" Response is {response.status_code} {response}"
                ),
                **self.context.log,
            )
            return None
        return response.json()

    def _deserialize_data(self) -> BookDatasource:
        """From the raw data build the final object instance.

        Args:
            book_data (dict[str, Any]): data of the book.
            authors_portraits (list[str]): the list with the authors's portraits.

        Returns:
            BookDatasource: the final instance of the object.
        """
        return BookDatasource(
            title=self._extract_value_from_key("volumeInfo.title"),
            authors=self._extract_value_from_key("volumeInfo.authors"),
            publishing=self._extract_value_from_key("volumeInfo.publisher"),
            published_on=self._parse_published_on(),
            cover=HttpUrl(
                self._extract_value_from_key("volumeInfo.imageLinks.thumbnail")
            ),
            plot=self._extract_value_from_key("volumeInfo.description"),
            languages=[self._extract_value_from_key("volumeInfo.language")],
            book_formats=[self._extract_value_from_key("volumeInfo.printType")],
        )

    def _parse_published_on(self) -> int | None:
        """Try to parse the published date.
        If it fails, return None.

        Returns:
            int | None: the year or None if not desumed.
        """
        date = self._extract_value_from_key("volumeInfo.publishedDate")
        if date is None:
            return None

        isodate_pattern = re.compile(r"^(?P<year>\d{4})-\d{2}-\d{2}$")
        is_isodate = isodate_pattern.match(date)
        if is_isodate:
            return int(is_isodate.group("year"))

        year_pattern = re.compile(r"^\d{4}$")
        is_year = year_pattern.match(date)
        if is_year:
            return int(date)

        return None

    def _extract_value_from_key(
        self,
        jsonpath: str,
    ) -> Any:
        """Given the json path, extract the value from the path from the data fetched from the APIs.

        Args:
            jsonpath (str): the path of intereset.

        Returns:
            str | None: the value, if the path is found.
        """
        expression = jmespath.compile(jsonpath)
        return expression.search(self._datasource)
