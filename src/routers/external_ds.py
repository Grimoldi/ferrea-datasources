from fastapi import APIRouter
from fastapi_utils.cbv import cbv
from starlette import status
from starlette.responses import JSONResponse

router = APIRouter()


@cbv(router)  # type: ignore
class DatasourcesCBV:
    @router.get("/book/{isbn}")
    def search_book(self, isbn: str) -> JSONResponse:
        print(f"Button hit!")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"defailt": f"You requested a search for isbn {isbn}"},
        )
