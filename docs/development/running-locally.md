# Running locally

To run a development server locally:

```bash
export PCDS_DSN=postgresql://user@host/dbname
poetry run uvicorn --reload --host 0.0.0.0 --port 8080 sdpb.wsgi:connexion_app
```

The server listens on `http://localhost:8080`. Interactive API documentation (Swagger UI) is available at `http://localhost:8080/ui`.
