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

## Important note

In [PR #33](https://github.com/pacificclimate/station-data-portal-backend/pull/33),
we pinned PyCDS to version 3.3.0 to make the backend compatible with the 
current state of the target databases (CRMP, metnorth), which have not been 
migrated to the revision required for the latest version, 4.0.0. 

The backend works correctly, but several unit tests fail because the ORM is 
still incorrectly defined in 3.3.0 (fixed in 4.0.0). The tests could 
perhaps be rejigged to work with the faulty ORM declarations, but why ... 
things will move past it and the "fix" undone. Better to have some failing 
tests.

The failing tests are marked xfail (actually, the failing fixture calls
`pytest.xfail`).

## Documentation

- [API Design](docs/api-design.md)
- [Installation](docs/installation.md)
- [Configuration](docs/configuration.md)
- [Production](docs/development.md)
- [Development](docs/development.md)
- [Unit testing](docs/unit-testing.md)
- [Performance testing](docs/performance-testing.md)
- [Supporting CRMP while it is behind PyCDS head revision](docs/supporting-crmp.md)
- [Release history](NEWS.md)

## Releasing

**Note**: We release on two branches, `master` and `crmp`, usually in lockstep.
For details on why and how, see 
[Supporting CRMP while it is behind PyCDS head revision](docs/supporting-crmp.md)
.

To create a versioned release:

1. Ensure that `crmp` has been appropriately updated. In most cases, this 
   means: 
   1. Check out `crmp`.
   2. Merge `master` into `crmp`. 
   3. Adjust the version of PyCDS in branch `crmp` as necessary to
  remain at a compatible release. (This usually means ensuring it is still
  at its old value, which at the time of writing is 3.2.0.)
   4. Run `pipenv lock` (or `pipenv install --dev`) and commit the updated
  `Pipfile.lock` to branch `crmp`.
2. Release on `crmp`:
   1. Check out `crmp`.
   2. Increment `__version__` in `setup.py` (version >=1, < 10).
   3. Add, commit, and tag, and push these changes:
      ```
      git add setup.py
      git commit -m "Bump crmp to version x.x.x
      git tag -a -m "x.x.x" x.x.x
      git push --follow-tags
      ```
3. Release on `master`:
   1. Check out `master`.
   2. Increment `__version__` in `setup.py` (version >= 10).
   3. Summarize the changes *for both
      branches* from the last releases in `NEWS.md`.
   4. Add, commit, and tag, and push these changes:
      ```
      git add setup.py NEWS.md
      git commit -m "Bump master to version x.x.x
      git tag -a -m "x.x.x" x.x.x
      git push --follow-tags
      ```
4. Have a beer or other refreshing beverage.
