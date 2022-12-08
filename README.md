# Station Data Portal Backend

[![Python CI](https://github.com/pacificclimate/station-data-portal-backend/actions/workflows/python-ci.yml/badge.svg)](https://github.com/pacificclimate/station-data-portal-backend/actions/workflows/python-ci.yml)
[![Docker Publishing](https://github.com/pacificclimate/station-data-portal-backend/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/pacificclimate/station-data-portal-backend/actions/workflows/docker-publish.yml)

The Station Data Portal Backend is a microservice providing metadata from a 
[PyCDS](https://github.com/pacificclimate/pycds) database.
The nominal client is the
[Station Data Portal](https://github.com/pacificclimate/station-data-portal) 
app, but it is not particularly tuned to this app.

At present, this service provides only metadata. Actual data downloads
from the database are provided by an instance of the PDP backend.

## Documentation

- [API Design](docs/api-design.md)
- [Installation](docs/installation.md)
- [Configuration](docs/configuration.md)
- [Production](docs/development.md)
- [Development](docs/development.md)
- [Unit testing](docs/unit-testing.md)
- [Performance testing](docs/performance-testing.md)
- [Release history](NEWS.md)

## Releasing

To create a versioned release:

1. Increment `__version__` in `setup.py` (version >= 10).
2. Summarize the changes from the last release in `NEWS.md`.
3. Add, commit, and tag, and push these changes:
   ```
   git add setup.py NEWS.md
   git commit -m "Bump master to version x.x.x
   git tag -a -m "x.x.x" x.x.x
   git push --follow-tags
   ```
