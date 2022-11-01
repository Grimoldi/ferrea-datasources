from fastapi import APIRouter
from fastapi_utils.cbv import cbv
from models.api_google import GoogleBooksAPI
from models.api_openlibrary import OpenLibraryAPI
from operations.service_google import GoogleBooksService
from operations.service_openlibrary import OpenLibraryService
from starlette import status
from starlette.responses import JSONResponse

router = APIRouter()


@cbv(router)
class DatasourcesCBV:
    """
    This class holds the endpoints for the app.
    Currently there are three endpoints, but just one is reported in OpenApi,
    since the other two are just tests for the
    """

    @router.get("/book/{isbn}")
    def search_book_datasource(self, isbn: str) -> JSONResponse:
        """
        This method performs the search of the book's data on external datasources.

        Args:
            isbn (str): the isbn of the desired book.

        Returns:
            JSONResponse: the data if found.
        """
        gb_api = GoogleBooksAPI("https://www.googleapis.com/books/v1")
        ol_service = GoogleBooksService(gb_api)
        book_data = ol_service.get_book_data(isbn)
        if book_data is None:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND, content={"detail": "not found"}
            )

        ol_api = OpenLibraryAPI("http://openlibrary.org/api/books")
        ol_service = OpenLibraryService(ol_api)
        author_portraits = ol_service.get_author_portrait(isbn)
        if author_portraits is not None:
            book_data.author_portrait = author_portraits[book_data.author[0]]

        return JSONResponse(
            status_code=status.HTTP_200_OK, content=book_data.serialize()
        )

    @router.get("/book/openlibrary/{isbn}")
    def search_book(self, isbn: str) -> JSONResponse:
        """
        This endpoint is a test endpoint for the response from openlibrary.
        It is not exposed in Openapi.

        Args:
            isbn (str): the isbn of the book

        Returns:
            JSONResponse: response from OpenLibrary API.
        """
        ol_api = OpenLibraryAPI("http://openlibrary.org/api/books")
        ol_service = OpenLibraryService(ol_api)
        author_portraits = ol_service.get_author_portrait(isbn)
        if author_portraits is not None:
            return JSONResponse(
                status_code=status.HTTP_200_OK, content=author_portraits
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND, content={"detail": "not found"}
            )

    @router.get("/book/googlebooks/{isbn}")
    def search_gb(self, isbn: str) -> JSONResponse:
        """
        This endpoint is a test endpoint for the response from googlebooks.
        It is not exposed in Openapi.

        Args:
            isbn (str): the isbn of the book

        Returns:
            JSONResponse: response from Google Book API.
        """
        gb_api = GoogleBooksAPI("https://www.googleapis.com/books/v1")
        gb_service = GoogleBooksService(gb_api)
        book_data = gb_service.test_book_data(isbn)
        if book_data is None:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND, content={"detail": "not found"}
            )

        return JSONResponse(status_code=status.HTTP_200_OK, content=book_data)
