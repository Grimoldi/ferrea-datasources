import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Response
from fastapi_utils.cbv import cbv
from ferrea.core.context import Context
from ferrea.core.header import FERRA_CORRELATION_HEADER, get_correlation_id
from ferrea.models.datasource import BookDatasource
from starlette import status
from starlette.responses import JSONResponse

from adapters.googlebooks import GoogleBooksRepository
from adapters.openlibrary import OpenLibraryRepository
from models.api_service import ApiService
from operations.data_search import fetch_data

router = APIRouter()


@cbv(router)
class DatasourcesCBV:
    """
    This class holds the endpoints for the app.
    Currently there are three endpoints, but just one is reported in OpenApi,
    since the other two are just tests for the
    """

    @router.get("/book/{isbn}")
    def search_book_datasource(
        self,
        isbn: str,
        _id: Annotated[uuid.UUID, Depends(get_correlation_id)],
        google_books_repository: Annotated[ApiService, Depends(GoogleBooksRepository)],
        openlibrary_repository: Annotated[ApiService, Depends(GoogleBooksRepository)],
        response: Response,
    ) -> BookDatasource | JSONResponse:
        """
        This method performs the search of the book's data on external datasources.

        Args:
            isbn (str): the isbn of the desired book.

        Returns:
            BookDatasource | JSONResponse: the serialization of the object if found or a message for resource not found.
        """
        context = Context(str(_id), "DTS")  # TODO: move to configuration management
        response.headers[FERRA_CORRELATION_HEADER] = str(_id)

        book_data = fetch_data(
            isbn,
            [google_books_repository, openlibrary_repository],
            context,
        )

        if book_data is None:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND, content={"detail": "not found"}
            )

        return book_data
