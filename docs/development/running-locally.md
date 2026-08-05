# Running locally

To run a development server locally:

```bash
export PCDS_DSN=postgresql://user@host/dbname
poetry run uvicorn --reload --host 0.0.0.0 --port 8080 sdpb.wsgi:connexion_app
```

The server listens on `http://localhost:8080`. Interactive API documentation (Swagger UI) is available at `http://localhost:8080/ui`.

To enable response caching locally with DragonflyDB:

```bash
docker run --rm -p 6379:6379 docker.dragonflydb.io/dragonflydb/dragonfly

export PCDS_DSN=postgresql://user@host/dbname
export CACHE_KEY_PREFIX=sdpb-pcds
export DRAGONFLY_HOST=localhost
export DRAGONFLY_PORT=6379
export CACHE_TTL_STATIONS=86400
export CACHE_TTL_HISTORIES=86400
export CACHE_TTL_FREQUENCIES=604800
export CACHE_TTL_NETWORKS=604800
export CACHE_TTL_VARIABLES=604800

poetry run uvicorn --reload --host 0.0.0.0 --port 8080 sdpb.wsgi:connexion_app
```

To disable caching explicitly during development:

```bash
export CACHE_ENABLED=false
```

If DragonflyDB is unavailable or misconfigured, the service falls back to direct
database reads instead of failing startup.
