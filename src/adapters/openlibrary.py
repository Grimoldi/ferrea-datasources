import os
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

OPENLIBRARY_API_BASE_URL = settings.openlibrary.api_url
OPENLIBRARY_COVER_BASE_URL = settings.openlibrary.cover_url

BOOK_DATA = "book"
AUTHOR_DATA = "author"
PORTRAIT_DATA = "cover"


@dataclass
class OpenLibraryRepository:
    """
    OpenLibrary Repository for query towards OpenLibrary API Service.

    Refer to https://openlibrary.org/ and https://openlibrary.org/developers/api for documentation.
    """

    context: Context
    name: str

    def search_for_book_info(self, isbn: str) -> BookDatasource | None:
        """Search on OpenLibrary the required isbn for book information as well as author portrait.

        Args:
            isbn (str): the isbn of the book.

        Returns:
            BookDatasource | None: the instance with the fetched information or None if not found.
        """
        self._datasource = dict()
        self._datasource[AUTHOR_DATA] = list()

        book = self._perform_isbn_search(isbn)
        if book is None:
            return None

        self._datasource[BOOK_DATA] = book
        authors = [x["key"] for x in book["authors"]]
        authors_portraits = list()

        for author in authors:
            author_id = os.path.basename(author)
            authors_portraits.append(self._perform_author_portrait_search(author_id))
            author_data = self._perform_author_search(author_id)
            self._datasource[AUTHOR_DATA].append(author_data)

        self._datasource[PORTRAIT_DATA] = authors_portraits

        return self._deserialize_data()

    def _perform_isbn_search(self, isbn: str) -> dict[str, Any] | None:
        """Perform a search on OpenLibrary to see if the isbn is known.

        Args:
            isbn (str): the isbn of the book.

        Returns:
            dict[str, Any] | None: the response from the service or None if book not found.
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        uri = f"{OPENLIBRARY_API_BASE_URL}/isbn/{isbn}"

        with httpx.Client() as client:
            response = client.get(
                uri,
                headers=headers,
                follow_redirects=True,
            )

        if not response.status_code == httpx.codes.OK:
            ferrea_logger.info(
                f"Unable to find {isbn} on Openlibrary. Response is {response.status_code} {response}",
                **self.context.log,
            )
            return None
        return response.json()

    def _perform_author_portrait_search(self, author_id: str) -> str | None:
        """Given an author olid (OpenLibrary ID), search the author portrait.
        If it is not found, a 404 will be raised from the service (thanks to default: False).
        In case it was found, just return the url of the image.

        Args:
            author_id (str): the OpenLibrary ID of the author.

        Returns:
            dict[str, Any] | None: the response from the service or None if portrait was not found.
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        uri = f"{OPENLIBRARY_COVER_BASE_URL}/a/olid/{author_id}-M.jpg"
        qp = {
            "default": False,
        }
        with httpx.Client() as client:
            response = client.get(
                uri,
                headers=headers,
                params=qp,
                follow_redirects=True,
            )

        if not response.status_code == httpx.codes.OK:
            ferrea_logger.info(
                f"Unable to find {author_id} on Openlibrary. Response is {response.status_code} {response.json()}",
                **self.context.log,
            )
            return None

        return uri

    def _perform_author_search(self, author_id: str) -> dict[str, Any] | None:
        """Given an author olid (OpenLibrary ID), search the author information.

        Args:
            author_id (str): the OpenLibrary ID of the author.

        Returns:
            dict[str, Any] | None: the response from the service or None if portrait was not found.
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        uri = f"{OPENLIBRARY_API_BASE_URL}/authors/{author_id}.json"
        with httpx.Client() as client:
            response = client.get(
                uri,
                headers=headers,
                follow_redirects=True,
            )

        if not response.status_code == httpx.codes.OK:
            ferrea_logger.info(
                f"Unable to find {author_id} on Openlibrary. Response is {response.status_code} {response.json()}",
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
            title=self._extract_value_from_key(f"{BOOK_DATA}.title"),
            authors=self._extract_value_from_key(f"{AUTHOR_DATA}[].name"),
            publishing=self._extract_value_from_key(f"{BOOK_DATA}.publishers[0]"),
            published_on=self._parse_published_on(),
            cover=HttpUrl(
                f"{OPENLIBRARY_COVER_BASE_URL}/b/id/{self._extract_value_from_key(f'{BOOK_DATA}.covers[0]')}-M.jpg"
            ),
            plot=self._extract_value_from_key(f"{BOOK_DATA}.first_sentence.value"),
            languages=[
                x.replace("/languages/", "")
                for x in self._extract_value_from_key(f"{BOOK_DATA}.languages[].key")
            ],
            book_formats=[
                x.replace("/type/", "")
                for x in [self._extract_value_from_key(f"{BOOK_DATA}.type.key")]
            ],
            authors_portrait=self._datasource[PORTRAIT_DATA],
        )

    def _parse_published_on(self) -> int | None:
        """Try to parse the published date.
        If it fails, return None.

        Returns:
            int | None: the year or None if not desumed.
        """
        date = self._extract_value_from_key(f"{BOOK_DATA}.publish_date")
        if date is None:
            return None

        isodate_pattern = re.compile(r"^(?P<year>\d{4})-\d{2}-\d{2}$")
        is_isodate = isodate_pattern.match(date)
        if is_isodate:
            return int(is_isodate.group("year"))

        year_pattern = re.compile(r".*[\s|\-](?P<year>\d{4}).*?")
        is_year = year_pattern.match(date)
        if is_year:
            return int(is_year.group("year"))

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

    @property
    def healthy(self) -> bool:
        """Health check towards the datasource."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "FastAPI HealthCheck",
        }
        uri = f"{OPENLIBRARY_API_BASE_URL}/health"

        with httpx.Client() as client:
            response = client.get(
                uri,
                headers=headers,
                follow_redirects=True,
            )

        if not response.status_code == httpx.codes.OK:
            ferrea_logger.info(
                (f"OpenLibrary probe failed with {response.status_code}"),
                **self.context.log,
            )
            return False
        return True
