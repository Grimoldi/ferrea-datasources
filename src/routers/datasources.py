from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response
from ferrea.core.context import Context
from ferrea.core.header import FERRA_CORRELATION_HEADER, get_correlation_id
from ferrea.models.datasource import BookDatasource
from starlette import status
from starlette.responses import JSONResponse

from adapters.googlebooks import GoogleBooksRepository
from adapters.openlibrary import OpenLibraryRepository
from configs import settings
from models.api_service import ApiService
from operations.data_search import fetch_data

router = APIRouter()


async def _build_context(request: Request) -> Context:
    """Build a context from the request.

    Args:
        request (Request): the HTTP Request.

    Returns:
        Context: the context of the call.
    """
    ferrea_correlation_id = request.headers.get(FERRA_CORRELATION_HEADER)
    correlation_id = await get_correlation_id(ferrea_correlation_id)
    return Context(str(correlation_id), settings.ferrea_app.name)


async def _openlibrary_factory(request: Request) -> OpenLibraryRepository:
    """Factory for the OpenLibraryRepository.

    Args:
        request (Request): the HTTP Request.

    Returns:
        OpenLibraryRepository: the repository.
    """
    context = await _build_context(request)
    return OpenLibraryRepository(context)


async def _google_factory(request: Request) -> GoogleBooksRepository:
    """Factory for the GoogleBooksRepository.

    Args:
        request (Request): the HTTP Request.

    Returns:
        GoogleBooksRepository: the repository.
    """
    context = await _build_context(request)
    return GoogleBooksRepository(context)


@router.get("/book/{isbn}", response_model=None)
def search_book_datasource(
    isbn: str,
    context: Annotated[Context, Depends(_build_context)],
    google_books_repository: Annotated[ApiService, Depends(_google_factory)],
    openlibrary_repository: Annotated[ApiService, Depends(_openlibrary_factory)],
    response: Response,
) -> BookDatasource | JSONResponse:
    """
    This function performs the search of the book's data on external datasources.

    Args:
        isbn (str): the isbn of the desired book.

    Returns:
        BookDatasource | JSONResponse: the serialization of the object if found or a message for resource not found.
    """
    response.headers[FERRA_CORRELATION_HEADER] = context.uuid
    headers = {FERRA_CORRELATION_HEADER: context.uuid}

    book_data = fetch_data(
        isbn,
        [google_books_repository, openlibrary_repository],
        context,
    )

    if book_data is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "not found"},
            headers=headers,
        )

    return book_data
