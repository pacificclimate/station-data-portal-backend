# Unit testing

## Docker test environment

To run the unit tests, you need a suitable environment, namely
one with a friendly version of PostgreSQL.

(Why? It does not seem to be easy to set up such an environment on Ubuntu 20.04 
or later; the default installation is PostgreSQL 13, and it does support
`plypythonu` (as opposed to `plpython3u`), which is required for the PyCDS 
database to be properly created (by migrating an empty database to the 
latest revision).
Therefore, we provide a Docker image which has PostgreSQL 10 installed, along
with compatible PostGIS and plpython extensions.)

This Docker test environment works in the same way as the one for PyCDS.

### Setup

For instructions on setting up your development environment to use this kind of
Docker test environment, see the PyCDS documentation 
[Project unit tests](https://github.com/pacificclimate/pycds/blob/master/docs/project-unit-tests.md)

If you have already set up for similar Docker test environments, all you will
need to do is to add permissions for the test environment user to your project
directory:

```
setfacl -Rm "g:dockremap1000:rwx" <directory>
```

### Usage

As in PyCDS, the necessary commands are encapsulated in a Makefile.
For details, please review the PyCDS instructions. Here is a brief summary:

To build the image (on first use of this project, and infrequently thereafter):

```
make local-pytest-image
```

To run the test container (to be left running for many tests):

```
make local-pytest-run
```

To run the tests in the container (at the container prompt):

```
pipenv run pytest tests
```

## PyCDS database migration in testing

TODO

