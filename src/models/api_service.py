from typing import Any, Protocol

import requests

ApiResponse = dict[Any, Any]


class ApiService(Protocol):
    """
    This class it's just a protocol about the methods an APIService class should implement.
    """

    def set_headers(self, headers: dict[str, Any]) -> None:
        """Set the headers."""
        ...

    def set_auth(self, key: str) -> None:
        """Set authorization."""
        ...

    def set_resource(self, endpoint: str) -> None:
        """Set the resource to fetch."""
        ...

    def set_query_string(self, query_string: dict[str, Any]) -> None:
        """Set the query string."""
        ...

    def set_base_url(self, base_url: str) -> None:
        """Set a new base url."""
        ...

    def get(self) -> requests.Response:
        """Get the data from the Api."""
        ...
