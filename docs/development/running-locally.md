# Running locally

To run a development server locally:

```bash
export FLASK_APP=sdpb.wsgi
export FLASK_ENV=development
export PCDS_DSN=postgresql://user@host/dbname
poetry run flask run
```
