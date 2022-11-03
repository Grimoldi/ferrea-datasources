# Ferrea-Datasources

Repo for Ferrea project. Dedicated to external datasources microservice.

This microservice is responsible for providing automatic data for a new book in the library circuit.

This microservice is made upon Fastapi that interacts with external API services (at the moment [OpenLibrary](https://openlibrary.org/developers/api) and [Google Books](https://developers.google.com/books)).

## Run as a docker container

``` bash
docker build --tag ferrea-datasources .

docker run --name ferrea-ds -d -p 8000:80 ferrea-datasources
```

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
