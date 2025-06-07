from pathlib import Path

from fastapi import FastAPI
from ferrea.core.oas import add_openapi_schema

from routers import datasources

models_path = Path("/oas/bundle.yaml")
app = FastAPI()
app = add_openapi_schema(app, models_path)

app.include_router(datasources.router)
