# Station Data Portal Backend

[![Python CI](https://github.com/pacificclimate/station-data-portal-backend/actions/workflows/python-ci.yml/badge.svg)](https://github.com/pacificclimate/station-data-portal-backend/actions/workflows/python-ci.yml)
[![Docker Publishing](https://github.com/pacificclimate/station-data-portal-backend/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/pacificclimate/station-data-portal-backend/actions/workflows/docker-publish.yml)

The Station Data Portal Backend is a microservice providing metadata from a 
[PyCDS](https://github.com/pacificclimate/pycds) database.
The nominal client is the
[Station Data Portal](https://github.com/pacificclimate/station-data-portal) 
app, but it is not particularly tuned to this app.

At present, this service provides only metadata. _Data_ download services are provided by an instance of the PDP backend.

## Documentation

- [API Design](docs/api-design.md)
- [Configuration](docs/configuration.md)
- [Production](docs/production.md)
- Development
  - [Caveats](docs/development/caveats.md)
  - [Installation](docs/development/installation.md)
  - [Running locally](docs/development/running-locally.md)
  - [Unit testing](docs/development/unit-testing.md)
  - [Performance testing](docs/development/performance-testing.md)
- [Release history](NEWS.md)

## Releasing

To create a versioned release:

1. Increment `version` in `pyproject.toml`.
2. Summarize the changes from the last release in `NEWS.md`.
3. Add, commit, and tag, and push these changes:
   ```
   git add setup.py NEWS.md
   git commit -m "Bump to version x.x.x
   git tag -a -m "x.x.x" x.x.x
   git push --follow-tags
   ```
