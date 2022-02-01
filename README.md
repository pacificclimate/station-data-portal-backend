# Station Data Portal Backend

TODO: Add badges

The Station Data Portal Backend is a microservice providing metadata from a 
[PyCDS](https://github.com/pacificclimate/pycds) database.
The nominal client is the
[Station Data Portal](https://github.com/pacificclimate/station-data-portal) 
app, but it is not particularly tuned to this app.

At present, this service provides only metadata. Actual data downloads
from the database are provided by an instance of the PDP backend.

## Documentation

- [Installation](docs/installation.md)
- [API Design](docs/api-design.md)
- [Development](docs/development.md)
- [Unit testing](docs/unit-testing.md)
- [Supporting CRMP while it is behind PyCDS head revision](docs/supporting-crmp.md)

## Releasing


