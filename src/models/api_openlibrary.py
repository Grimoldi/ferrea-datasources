import logging
from typing import Any

import requests
from attrs import define, field
from ferrea.observability import init_logger


@define
class OpenLibraryAPI:
    """
    This class it's the implementation of APIService regarding OpenLibrary APIs.
    """

    base_url: str
    headers: dict[str, Any] = field(factory=dict)
    query_string: dict[str, Any] = field(factory=dict)
    endpoint: str = field(init=False)
    logger: logging.Logger = field(init=False, factory=init_logger)

    def set_headers(self, headers: dict[str, Any]) -> None:
        """Set the headers."""
        self.headers = headers

    def set_auth(self, key: str) -> None:
        """Set authorization."""
        raise NotImplementedError()

    def set_resource(self, endpoint: str) -> None:
        """Set the resource to fetch."""
        self.endpoint = endpoint

    def set_query_string(self, query_string: dict[str, Any]) -> None:
        """Set the query string."""
        self.query_string = query_string

    def set_base_url(self, base_url: str) -> None:
        """Set a new base url."""
        self.base_url = base_url

    def get(self) -> requests.Response:
        """Get the data from the Api."""
        url = f"{self.base_url}/{self.endpoint}"
        self.logger.debug(f"{url=}, {self.query_string=}, {self.headers=}")
        response = requests.get(url=url, params=self.query_string, headers=self.headers)

        return response
