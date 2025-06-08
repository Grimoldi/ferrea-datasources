from pathlib import Path

import uvicorn
from fastapi import FastAPI
from ferrea.core.oas import add_openapi_schema
from ferrea.observability.logs import setup_logger

from configs import settings
from routers import datasources


def app() -> FastAPI:
    """Setup the app with custom logic."""
    setup_logger()
    app = FastAPI()
    if settings.ferrea_app.oas_path is not None:
        app = add_openapi_schema(app, Path(settings.ferrea_app.oas_path))

    app.include_router(datasources.router)

    return app


if __name__ == "__main__":
    uvicorn.run("app:app", port=8080, log_level=None, factory=True, access_log=False)
