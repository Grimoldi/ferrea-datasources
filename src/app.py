import os
from pathlib import Path

from ferrea import api

from routers import external_ds

ferrea_app = os.environ["FERREA_APP"]
models_path = Path("/oas/bundle.yaml")
app = api.init_api(models_path=models_path, ferrea_app=ferrea_app)

app.include_router(external_ds.router)
