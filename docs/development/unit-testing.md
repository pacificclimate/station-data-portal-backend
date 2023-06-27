# Unit testing

Unit tests are entirely self-contained: they set up a transient test database,
populate it, and run tests against it. They need no connection to external
databases (unlike performance testing).

Therefore, unit tests are suitable for CI or other cloud-based execution.

Unit test code is mainly in `tests/unit/`; it also makes use of common helper
functions and `conftest.py` in `tests/`.

## PyCDS database migration in testing

TODO

