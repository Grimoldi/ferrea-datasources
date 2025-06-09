import json
from typing import Annotated

from fastapi import APIRouter, Depends
from ferrea.core.context import Context
from ferrea.core.header import FERRA_CORRELATION_HEADER
from starlette import status
from starlette.responses import JSONResponse

from models.api_service import ApiService
from operations.data_search import fetch_data

from ._builders import _build_context, _google_factory, _openlibrary_factory

router = APIRouter(prefix="/api/v1")


@router.get("/book/{isbn}", response_model=None)
async def search_book_datasource(
    isbn: str,
    context: Annotated[Context, Depends(_build_context)],
    google_books_repository: Annotated[ApiService, Depends(_google_factory)],
    openlibrary_repository: Annotated[ApiService, Depends(_openlibrary_factory)],
) -> JSONResponse:
    """
    This function performs the search of the book's data on external datasources.

    Args:
        isbn (str): the isbn of the desired book.

    Returns:
        JSONResponse: the serialization of the object if found or a message for resource not found.
    """
    headers = {
        FERRA_CORRELATION_HEADER: context.uuid,
        "content-type": "application/json",
    }

    book_data = fetch_data(
        isbn,
        [google_books_repository, openlibrary_repository],
        context,
    )

    if book_data is None:
        status_code = status.HTTP_404_NOT_FOUND
        results = []
    else:
        status_code = status.HTTP_200_OK
        results = [json.loads(book_data.model_dump_json())]

    return JSONResponse(
        status_code=status_code,
        content={
            "items": len(results),
            "result": results,
        },
        headers=headers,
    )
