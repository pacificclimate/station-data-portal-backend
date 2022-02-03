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

**Note**: We release on two branches, `master` and `crmp`, usually in lockstep.
For details, see [Supporting CRMP while it is behind PyCDS head revision](docs/supporting-crmp.md)

To create a versioned release:

1. Ensure that `crmp` has been appropriately updated. In most cases, this 
   means merging `master` into it.
2. Update `crmp`:
   1. Check out `crmp`.
   2. Increment `__version__` in `setup.py` (version >=1, < 3).
   3. Add, commit, and tag, and push these changes:
      ```
      git add setup.py
      git commit -m "Bump crmp to version x.x.x
      git tag -a -m "x.x.x" x.x.x
      git push --follow-tags
      ```
3. Update `master`:
   1. Check out `master`.
   2. Increment `__version__` in `setup.py` (version >= 3).
   3. Summarize the changes *for both
      branches* from the last releases in `NEWS.md`.
   4. Add, commit, and tag, and push these changes:
      ```
      git add setup.py NEWS.md
      git commit -m "Bump master to version x.x.x
      git tag -a -m "x.x.x" x.x.x
      git push --follow-tags
      ```

```
git add setup.py NEWS.md
git commit -m"Bump to version x.x.x"
git tag -a -m"x.x.x" x.x.x
git push --follow-tags
```

