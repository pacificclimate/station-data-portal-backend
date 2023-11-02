# Running locally

To run a development server locally:

```bash
export PCDS_DSN=postgresql://user@host/dbname
export FLASK_APP=sdpb.wsgi
export FLASK_ENV=development
poetry run flask run
```
