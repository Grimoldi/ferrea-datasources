from pathlib import Path

from dynaconf.typed import Annotated, DictValue, Dynaconf, Options
from dynaconf.typed.validators import Validator

config_dir = Path(__file__).parent


class Openlibrary(DictValue):
    api_url: Annotated[str, Validator(startswith="https://")]
    cover_url: Annotated[str, Validator(startswith="https://")]


class Google(DictValue):
    api_url: Annotated[str, Validator(startswith="https://")]


class App(DictValue):
    name: str
    debug: bool = False


class FerreaSettings(Dynaconf):
    app: App = App()  # type: ignore
    google: Google = Google()  # type: ignore
    openlibrary: Openlibrary = Openlibrary()  # type: ignore

    dynaconf_options = Options(
        envvar_prefix="FERREA",
        settings_files=["settings.toml", ".secrets.toml"],
        root_path=config_dir,
    )


settings = FerreaSettings()
