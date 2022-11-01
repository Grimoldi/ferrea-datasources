# ferrea-datasources

Repo for Ferrea project. Dedicated to external datasources microservice.

## Run as a docker container

docker build --tag ferrea-datasources .

docker run --name ferrea-ds -d -p 8000:80 ferrea-datasources
