# Ferrea-Datasources

[![Python formatting](https://github.com/Grimoldi/ferrea-datasources/actions/workflows/format.yaml/badge.svg)](https://github.com/Grimoldi/ferrea-datasources/actions/workflows/format.yaml)
[![Docstrings](https://github.com/Grimoldi/ferrea-datasources/actions/workflows/docstrings.yaml/badge.svg)](https://github.com/Grimoldi/ferrea-datasources/actions/workflows/docstrings.yaml)
[![Testing](https://github.com/Grimoldi/ferrea-datasources/actions/workflows/testing.yaml/badge.svg)](https://github.com/Grimoldi/ferrea-datasources/actions/workflows/testing.yaml)[![Build](https://github.com/Grimoldi/ferrea-datasources/actions/workflows/build.yaml/badge.svg)](https://github.com/Grimoldi/ferrea-datasources/actions/workflows/build.yaml)

Repo for Ferrea project. Dedicated to external datasources microservice.

This microservice is responsible for providing automatic data for a new book in the library circuit.

This microservice is made upon Fastapi that interacts with external API services (at the moment [OpenLibrary](https://openlibrary.org/developers/api) and [Google Books](https://developers.google.com/books)).

## Run as a docker container

``` bash
docker run \
  --name ferrea-ds \
  --detach \
  --publish 8080:80 \
  --env FERREA_APP=datasources \
  grimoldi/ferrea-datasources:<tag>
```

Access it on [http://127.0.0.1:8080/docs/datasources](http://127.0.0.1:8080/docs/datasources), for example.

## Run on Kubernetes

Apply the manifests you can find under k8s folder.

``` bash
kubectl apply -f k8s/
```

## Web service structure

The web service has three distinct layers:

- web api layer: the routing of the api (./src/routers folder).
- business logic layer: the logic under the hood (./src/operations folder).
- data layer: how to access to the data (./src/models folder).

### Openapi Schema

You can find the OpenApi exposed under the */docs/datasources* endpoint.

The OpenApi definitions are stored under the ./src/definitions folder.
