from pathlib import Path

import yaml
from fastapi import FastAPI
from yamlinclude import YamlIncludeConstructor

from routers import external_ds

ferrea_app = "datasources"
app = FastAPI(
    debug=True,
    openapi_url=f"/openapi/{ferrea_app}.json",
    docs_url=f"/docs/{ferrea_app}",
)

models_path = Path(__file__).parent / "definitions"
YamlIncludeConstructor.add_to_loader_class(
    loader_class=yaml.FullLoader, base_dir=models_path
)
oas_path = models_path / "oas.yaml"
oas_doc = yaml.load(oas_path.read_text(), Loader=yaml.FullLoader)

app.openapi = lambda: oas_doc
app.include_router(external_ds.router)
