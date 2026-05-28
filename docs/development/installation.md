## Installation for development

## Clone the project

```bash
git clone https://github.com/pacificclimate/station-data-portal-backend
```

## Option 1: Docker (recommended)

The simplest way to run the app locally is with Docker Compose:

```bash
cd docker
docker compose up
```

The container exposes the API on port 8084. See the `docker/` directory for configuration options.

## Option 2: Local installation with Poetry

Requires Python **>=3.9, <3.14**.

### Install Poetry package manager

We use [Poetry](https://python-poetry.org/) to manage package dependencies. To install Poetry, use the [official installer](https://python-poetry.org/docs/#installation):

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### Install the project

```bash
poetry install
```

Poetry creates a virtual environment automatically. If you need to target a specific Python version within the supported range, use Poetry's [environment management](https://python-poetry.org/docs/managing-environments/) commands to switch between them.

## Production deployment

For production, run gunicorn with the `UvicornWorker` to serve the ASGI app:

```bash
gunicorn \
  -b :8000 \
  -k uvicorn.workers.UvicornWorker \
  sdpb.wsgi:connexion_app
```

Gunicorn settings (workers, threads, timeout, etc.) can be controlled via environment variables prefixed with `GUNICORN_` — for example, `GUNICORN_WORKERS=4`. See `docker/gunicorn.conf` for details.

The Docker image handles this automatically; see [Docker (recommended)](#option-1-docker-recommended) above.
