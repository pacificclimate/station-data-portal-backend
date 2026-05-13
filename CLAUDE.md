# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Station Data Portal Backend (`sdpb`) is a Python microservice that serves metadata from a [PyCDS](https://github.com/pacificclimate/pycds) (PCDS/CRMP) climate station database. It provides read-only REST endpoints for networks, stations, histories, variables, observations, and weather data. The nominal client is the [Station Data Portal](https://github.com/pacificclimate/station-data-portal) frontend.

## Commands

**Install dependencies** (uses Poetry with a custom PCIC PyPI source):
```bash
poetry install
```

**Run the development server** (Connexion 3 is ASGI — use uvicorn, not `flask run`):
```bash
export PCDS_DSN=postgresql://user@host/dbname
poetry run uvicorn --reload --host 0.0.0.0 --port 8080 sdpb.wsgi:connexion_app
```

**Run all unit tests** (self-contained; spins up a transient PostgreSQL instance):
```bash
poetry run pytest tests/unit
```

**Run a single test file:**
```bash
poetry run pytest tests/unit/api/test_stations.py
```

**Run performance tests** (requires a real CRMP database connection):
```bash
PCDS_DSN=postgresql://... poetry run pytest tests/performance
```

**Format code** (Black is pinned at 25.1.0 — do not upgrade without re-running on the whole codebase):
```bash
poetry run black sdpb tests
```

## Architecture

### App factory and entry points

- [sdpb/__init__.py](sdpb/__init__.py) — `create_app(config_override={})` builds the Connexion 3 `FlaskApp`, wires up Flask-SQLAlchemy, Flask-Compress, and a CORS middleware, then registers the OpenAPI spec. Returns `(connexion_app, flask_app, app_db)`.
- [sdpb/wsgi.py](sdpb/wsgi.py) — ASGI entry point; calls `create_app()` and exposes `connexion_app` for uvicorn/gunicorn.

### OpenAPI routing

[sdpb/openapi/api-spec.yaml](sdpb/openapi/api-spec.yaml) is the single source of truth for the API. Connexion reads it and routes each request to the Python function named by `operationId` (e.g. `sdpb.api.networks.collection`). Every new endpoint requires both a spec entry and a matching Python handler.

### API handler modules (`sdpb/api/`)

Each resource has its own module with `collection()` and `single()` top-level functions (matched by `operationId` in the spec):

| Module | Endpoints |
|---|---|
| `networks.py` | `/networks`, `/networks/{id}` |
| `stations.py` | `/stations`, `/stations/{id}` |
| `histories.py` | `/histories`, `/histories/{id}` |
| `variables.py` | `/variables`, `/variables/{id}` |
| `frequencies.py` | `/frequencies` |
| `observations.py` | `/observations/counts` |
| `station_variables.py` | `/stations/{id}/variables`, `/stations/{id}/variables/{var_id}`, and their observations |
| `crmp_network_geoserver.py` | `/crmp_network_geoserver` |
| `weather/monthly/baseline.py` | `/weather/monthly/baseline/{variable};{month}` |
| `weather/monthly/weather.py` | `/weather/monthly/weather/{variable};{year}-{month}` |

All handlers call `get_app_session()` (from `sdpb`) to get the database session — **never** import the module-level `app_db` global directly, or tests will fail because the global is captured before it is initialized.

### Shared utilities

- [sdpb/util/query.py](sdpb/util/query.py) — common SQLAlchemy 2.0 query helpers: `get_all_histories_etc_by_station`, `get_all_vars_by_hx`, `add_station_network_publish_filter`, `add_province_filter`.
- [sdpb/util/representation.py](sdpb/util/representation.py) — serialization helpers: `date_rep`, `float_rep`, `is_expanded`, `parse_date`, `obs_stats_rep`.
- [sdpb/timing.py](sdpb/timing.py) — `log_timing` context manager for optional performance logging.

### Data filtering rules

All station/history/network endpoints silently filter results:
- Only networks where `Network.publish == True` are returned.
- Stations are only returned if they have at least one associated `History` with a corresponding `StationObservationStats` record.
- Province filtering is applied via the shared `add_province_filter` helper when the `provinces` query parameter is present.

### Configuration

The app is configured by a single environment variable:

- `PCDS_DSN` — PostgreSQL DSN for the PCDS/CRMP database (default: `postgresql://httpd@db.pcic.uvic.ca/crmp`)

See `.env.example` for local development values.

## Testing

Unit tests are fully self-contained. They use `testing.postgresql` to spin up a throwaway Postgres instance and apply PyCDS Alembic migrations before each test package runs.

- [tests/conftest.py](tests/conftest.py) — base `app_parts`, `flask_app`, `app_db` fixtures (package-scoped).
- [tests/unit/api/conftest.py](tests/unit/api/conftest.py) — database initialization, migration, and all test data fixtures (networks, stations, histories, variables, observations, climate values).
- [tests/helpers/helpers.py](tests/helpers/helpers.py) — `groupby_dict` and `find` helper functions used in expected-result fixtures.

In Connexion 3 (ASGI), the Flask route map is built lazily. Tests must call `connexion_app.middleware._build_middleware_stack()` after `create_app()` so that `url_for()` works — this is done in the `app_parts` fixture.

Primary keys are set explicitly in test fixtures because `pycds.StationObservationStats` lacks a relationship attribute for `History`, preventing SQLAlchemy from resolving foreign keys for in-memory objects.

## Deployment

Docker: multi-stage build in [docker/Dockerfile](docker/Dockerfile) produces a minimal Ubuntu 24.04 image. Runs gunicorn with `uvicorn.workers.UvicornWorker`.

```bash
# Build and run with docker compose
cd docker
docker compose up
```

The container exposes port 8000 (mapped to 8084 in the compose file). Gunicorn settings are controlled by environment variables prefixed `GUNICORN_`.

## Swagger UI

When the dev server is running, interactive API documentation is available at `http://localhost:8080/ui`.

## Releasing

1. Bump `version` in [pyproject.toml](pyproject.toml).
2. Summarize changes in [NEWS.md](NEWS.md).
3. Commit, tag, and push: `git tag -a -m "x.x.x" x.x.x && git push --follow-tags`.
