import os
from pathlib import Path

from fastapi import FastAPI
from ferrea.core.oas import add_openapi_schema

from routers import datasources

ferrea_app = os.environ["FERREA_APP"]  # TODO: move to configuration management
models_path = Path("/oas/bundle.yaml")
app = FastAPI()
app = add_openapi_schema(app, models_path)

app.include_router(datasources.router)
