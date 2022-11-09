import logging
import re
from typing import Any

import jmespath
import requests
from attr import define, field
from ferrea.models import Datasource
from ferrea.observability import init_logger
from models.api_service import ApiResponse, ApiService


@define
class GoogleBooksService:
    """
    This class holds how to search and what to return for any calls related to Google Books APIs.
    """

    googlebooks_api: ApiService
    isbn: str = field(init=False)
    logger: logging.Logger = field(init=False, factory=init_logger)
    gb_response: Any = field(init=False)

    def get_book_data(self, isbn: str) -> Datasource | None:
        """
        This method queries Google Books API in order to look for the book based on its isbn.
        Please note that Google states that the result could be depending upon the localization.
        For further reading, refer to: https://developers.google.com/books/docs/v1/using#UserLocation

        Args:
            isbn (str): the isbn of the book.

        Returns:
            ApiResponse | None: the data found.
        """
        self.isbn = isbn
        gb_search_response = self._search_book()
        if not gb_search_response.ok or not "items" in gb_search_response.json():
            self.logger.warning(f"Unable to find book on GB for isbn: {isbn}")
            return  # book not found

        book_id = gb_search_response.json()["items"][0]["id"]
        gb_book_response = self._get_book(book_id)

        if not gb_book_response.ok:
            self.logger.warning(f"Unable to find book on GB for isbn: {isbn}")
            return  # book not found

        self.gb_response = gb_book_response.json()
        return self._parse_gb_data()

    def test_book_data(self, isbn: str) -> ApiResponse | None:
        """
        This method queries Google Books API in order to look for the book based on its isbn.
        Please note that Google states that the result could be depending upon the localization.
        For further reading, refer to: https://developers.google.com/books/docs/v1/using#UserLocation
        This method is a subset of get_book_data and will only display the returns from Google Api for debugging purpouse.

        Args:
            isbn (str): the isbn of the book.

        Returns:
            ApiResponse | None: the data found.
        """
        self.isbn = isbn
        gb_search_response = self._search_book()
        if not gb_search_response.ok or not "items" in gb_search_response.json():
            self.logger.warning(f"Unable to find book on GB for isbn: {isbn}")
            return  # book not found

        book_id = gb_search_response.json()["items"][0]["id"]
        return self._get_book(book_id).json()

    def _search_book(self) -> requests.Response:
        """
        This method performs the get towards the public endpoint of google book.
        It searches for the book, based on its isbn.

        Returns:
            requests.Response: the response from google api.
        """
        headers = {
            "Content-Type": "application/json",
        }
        qs = {"q": f"isbn:{self.isbn}", "projection": "lite"}
        self.googlebooks_api.set_headers(headers)
        self.googlebooks_api.set_query_string(qs)
        self.googlebooks_api.set_resource("volumes")

        response = self.googlebooks_api.get()
        if not response.ok:
            response = requests.Response()
            response.status_code = 404
            response.reason = "not_found"

        return response

    def _get_book(self, book_id: str) -> requests.Response:
        """
        This method performs the get of the book from Google Books api.

        Args:
            book_id (str): Google Books id for the searched book.

        Returns:
            requests.Request: the response from google api.
        """
        self.googlebooks_api.set_resource(f"volumes/{book_id}")

        response = self.googlebooks_api.get()
        if not response.ok:
            response = requests.Response()
            response.status_code = 404
            response.reason = "not_found"

        return response

    def _parse_gb_data(self) -> Datasource:
        """
        This function parses the Google Books response in order to construct a Datasource object.

        Args:
            gb_response (requests.Response): the response from Google Books api.

        Returns:
            Datasource: the deserialized object.
        """
        ds = Datasource(title=self._parse_title(), author=self._parse_authors())
        ds.publishing = self._parse_publishing()
        # ds.published_on = self._parse_published_on()  # type: ignore
        ds.cover = self._parse_cover()
        ds.plot = self._parse_plot()
        ds.language = self._parse_language()
        ds.book_format = self._parse_book_format()

        return ds

    def _parse_response(self, dict_path: str) -> Any:
        """
        This method uses jmespath to get the data searched.

        Args:
            expression (str): the expression to be used to scan the response.

        Returns:
            Any: the result of the search.
        """
        expression = jmespath.compile(dict_path)
        return expression.search(self.gb_response)

    def _parse_title(self) -> str:
        """
        This method search for the book title.

        Returns:
            str: the title.
        """
        return self._parse_response("volumeInfo.title")

    def _parse_authors(self) -> list[str]:
        """
        This method search for the book authors.

        Returns:
            list[str]: list of the authors.
        """
        return self._parse_response("volumeInfo.authors")

    def _parse_publishing(self) -> str:
        """
        This method search for the book publishing.

        Returns:
            str: the publishing.
        """
        return self._parse_response("volumeInfo.publisher")

    def _parse_published_on(self) -> int | None:
        """
        This method search for the book published date.

        Returns:
            int: the year of publishing.
        """
        date = self._parse_response("volumeInfo.publishedDate")
        if date is None:
            return None

        isodate_pattern = re.compile(r"^(?P<year>\d{4})-\d{2}-\d{2}$")
        year_pattern = re.compile(r"^\d{4}$")
        is_isodate = isodate_pattern.match(date)
        is_year = year_pattern.match(date)
        if is_isodate:
            return int(is_isodate.group("year"))
        elif is_year:
            return int(date)
        else:
            return

    def _parse_cover(self) -> str:
        """
        This method search for the book cover.
        It gets the thumbnail format.

        Returns:
            str: the cover.
        """
        return self._parse_response("volumeInfo.imageLinks.thumbnail")

    def _parse_plot(self) -> str:
        """
        This method search for the book plot.

        Returns:
            str: the plot.
        """
        return self._parse_response("volumeInfo.description")

    def _parse_language(self) -> list[str]:
        """
        This method search for the book languages.

        Returns:
            list[str]: the list of languages.
        """
        return self._parse_response("volumeInfo.imageLinks.language")

    def _parse_book_format(self) -> str:
        """
        This method search for the book reading format.

        Returns:
            str: the reading format.
        """
        return self._parse_response("volumeInfo.printType")
