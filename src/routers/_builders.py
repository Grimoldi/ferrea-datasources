from fastapi import Request
from ferrea.core.context import Context
from ferrea.core.header import FERRA_CORRELATION_HEADER, get_correlation_id

from adapters.googlebooks import GoogleBooksRepository
from adapters.openlibrary import OpenLibraryRepository
from configs import settings


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
    return OpenLibraryRepository(
        context, "OpenLibrary"
    )  # TODO move to config management


async def _google_factory(request: Request) -> GoogleBooksRepository:
    """Factory for the GoogleBooksRepository.

    Args:
        request (Request): the HTTP Request.

    Returns:
        GoogleBooksRepository: the repository.
    """
    context = await _build_context(request)
    return GoogleBooksRepository(
        context, "GoogleBooks"
    )  # TODO move to config management
