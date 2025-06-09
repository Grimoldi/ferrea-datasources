from typing import Annotated

from fastapi import APIRouter, Depends
from starlette import status
from starlette.responses import JSONResponse

from models.api_service import ApiService
from operations.probe import check_health

from ._builders import _google_factory, _openlibrary_factory

router = APIRouter()


@router.get("/_/ready", response_model=None)
async def readiness() -> JSONResponse:
    """
    This function serves as readiness probe.

    Returns:
        JSONResponse: a response.
    """
    headers = {
        "content-type": "application/json",
    }

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "ready": "Healthy",
        },
        headers=headers,
    )


@router.get("/_/health", response_model=None)
async def liveness(
    google_books_repository: Annotated[ApiService, Depends(_google_factory)],
    openlibrary_repository: Annotated[ApiService, Depends(_openlibrary_factory)],
) -> JSONResponse:
    """This function serves as readiness probe.

    Returns:
        JSONResponse: a response.
    """
    headers = {
        "content-type": "application/json",
    }

    health = check_health([google_books_repository, openlibrary_repository])

    if health["status"] == "Healthy":
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=health,
            headers=headers,
        )

    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content=health,
        headers=headers,
    )
