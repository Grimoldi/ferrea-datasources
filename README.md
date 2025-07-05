# Ferrea-Datasources

[![Python formatting](https://github.com/Grimoldi/ferrea-datasources/actions/workflows/format.yaml/badge.svg)](https://github.com/Grimoldi/ferrea-datasources/actions/workflows/format.yaml)
[![Docstrings](https://github.com/Grimoldi/ferrea-datasources/actions/workflows/docstrings.yaml/badge.svg)](https://github.com/Grimoldi/ferrea-datasources/actions/workflows/docstrings.yaml)
[![Testing](https://github.com/Grimoldi/ferrea-datasources/actions/workflows/testing.yaml/badge.svg)](https://github.com/Grimoldi/ferrea-datasources/actions/workflows/testing.yaml)[![Build](https://github.com/Grimoldi/ferrea-datasources/actions/workflows/build.yaml/badge.svg)](https://github.com/Grimoldi/ferrea-datasources/actions/workflows/build.yaml)[![OpenAPI definition linting](https://github.com/Grimoldi/ferrea-datasources/actions/workflows/oas-lint.yaml/badge.svg)](https://github.com/Grimoldi/ferrea-datasources/actions/workflows/oas-lint.yaml)

Repo related to my [Ferrea](https://github.com/Grimoldi/ferrea) personal project, dedicated for the `Datasource` microservice.

This microservice is responsible for fetching data about a book, avoiding data entry.

It queries external API services (at the moment [OpenLibrary](https://openlibrary.org/developers/api) and [Google Books](https://developers.google.com/books)).

## Configuration

The project uses [Dynaconf](https://www.dynaconf.com/) for its configuration.

Apart from manually change/override [settings.toml](./src/configs/settings.toml) and [.secrets.toml](./src/configs/.secrets.toml), every key can be injected as an env var. Just prefix it with `FERREA_` (eg `FERREA_FERREA_APP__NAME=MY_NAME`) to change the value of the shortname (under the variable `settings.ferrea_app.name`).

Refer to the [documentation](https://www.dynaconf.com/envvars/#custom-prefix) for more details.

## Run on Kubernetes

The application is meant to be run on Kubernetes.

Although previously I had some manifest for the Deployment creation and so on, I decided to remove that from here, and later use a repository to more adhere to the GitOPS principles.

### Openapi Schema

You can find the OpenApi exposed under the `/docs` endpoint.

The OpenApi definitions are stored under the [oas (OpenApi Schema) folder](./oas).
