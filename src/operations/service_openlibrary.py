import logging
import os
from typing import Any

import jmespath
import requests
from attr import define, field
from ferrea.observability import init_logger
from models.api_service import ApiService


@define
class OpenLibraryService:
    """
    This class holds how to search and what to return for any calls related to OpenLibrary APIs.
    """

    openlibary_api: ApiService
    isbn: str = field(init=False)
    logger: logging.Logger = field(init=False, factory=init_logger)

    def get_author_portrait(self, isbn: str) -> dict[str, str] | None:
        """
        This method queries OpenLibrary public API in order to search for the author portrait.
        It will query OpenLibrary public API for the book; from it, it derives the author.
        From the authors resource it gets the author an the portrait url.

        Args:
            isbn (str): isbn of the book.

        Returns:
            dict[str, str] | None: a dictionary with every author of the book and its portrait url.
        """
        self.isbn = isbn
        ol_response = self._search_book()
        if not ol_response.ok:
            self.logger.warning(f"Unable to find book on OL for isbn: {isbn}")
            return  # book not found

        authors = self._parse_for_book_authors(ol_response.json())

        if authors is None:
            self.logger.warning(f"Unable to find authors on OL for isbn: {isbn}")
            return  # authors not found

        portraits_url: dict[str, str] = dict()
        for author in authors:
            author_url = self._search_author_portrait(author_olid=author["key"])
            if not author_url.ok:  # author's portrait not found
                self.logger.warning(
                    f"Unable to find author portrait on OL for isbn: {isbn}"
                )
                continue

            # removing query string and adding to final dict
            portraits_url[author["name"]] = author_url.url.split("?")[0]

        if portraits_url != dict():
            return portraits_url

    def _search_book(self) -> requests.Response:
        """
        This method performs the get towards the public endpoint of openlibrary.
        It searches for the book, based on its isbn.

        Returns:
            requests.Response: the response of openlibrary api.
        """
        headers = {
            "Content-Type": "application/json",
        }
        uri = "http://openlibrary.org/api"
        qs = {
            "bibkeys": f"ISBN:{self.isbn}",
            "jscmd": "details",
            "format": "json",
        }
        self.openlibary_api.set_headers(headers)
        self.openlibary_api.set_base_url(uri)
        self.openlibary_api.set_query_string(qs)
        self.openlibary_api.set_resource("books")

        response = self.openlibary_api.get()
        if not response.ok:
            response = requests.Response()
            response.status_code = 404
            response.reason = "not_found"

        return response

    def _parse_for_book_authors(
        self, ol_response: dict[str, Any]
    ) -> list[dict[str, str]] | None:
        """
        This method parse the response from openlibrary (OL) and looks for the authors.

        Args:
            ol_response (dict[str, Any]): the response from ol api.

        Returns:
            list[dict[str, str]] | None: the list of the authors, if found.
            The list will contains a dictionary with two keys, "name" and "key" (the latter with the url of the author).
        """
        authors_exp = jmespath.compile(f"*.details.authors")
        book_authors: list[list[dict[str, str]]] = authors_exp.search(ol_response)

        for authors in book_authors:
            return authors

    def _search_author_portrait(self, author_olid: str) -> requests.Response:
        """
        This method performs the get towards the public endpoint of openlibrary.
        It searches for the author portrait, based on its olid (OpenLibrary ID).

        Args:
            author_olid (str): the olid of the author.

        Returns:
            requests.Response: the response of openlibrary api.
        """
        headers = {
            "Content-Type": "application/json",
        }
        uri = "http://covers.openlibrary.org/a/olid"
        # author olid is in form of /authors/<olid>. Getting rid of unnecessary data
        resource = f"{os.path.basename(author_olid)}-M.jpg"
        # by default if not found it will return 200 and a blank image. Changing to false will return a 404
        qs = {"default": False}
        self.openlibary_api.set_headers(headers)
        self.openlibary_api.set_base_url(uri)
        self.openlibary_api.set_resource(resource)
        self.openlibary_api.set_query_string(qs)

        return self.openlibary_api.get()
