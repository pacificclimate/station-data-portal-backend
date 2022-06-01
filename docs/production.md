# Production

## Docker

We currently deploy all apps using Docker.
This project contains [Docker infrastructure](../docker) and a
[GitHub action](../.github/workflows/docker-publish.yml) that automatically
builds and tags a Docker image on each commit. The image name is
`pcic/station-data-portal-backend`.

Note: The Docker image runs Gunicorn as the HTTP server container.

## Configuration

See [Configuration](configuration.md).

Note: Production deployments also configure Gunicorn and application logging. 

## Deployment

See the contents of the [`docker`](../docker) directory for an example of how
to run the Docker image. 
This directory also includes template Gunicorn and logging configuration 
files.

