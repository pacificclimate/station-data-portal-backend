## Installation for development

## Clone the project

```bash
$ git clone https://github.com/pacificclimate/station-data-portal-backend
```

It is best practice to install using a virtual environment.
We use [`pipenv`](https://pipenv.pypa.io/en/latest/)
to manage dependencies and create a virtual environment.

### Install Poetry package manager

We use [Poetry](https://python-poetry.org/) to manage package dependencies
and installation.
To install Poetry, we recommend using the
[official installer](https://python-poetry.org/docs/#installation):

```text
curl -sSL https://install.python-poetry.org | python3 -
```

## Install the project using Poetry

You can install the project in any version of Python >= 3.7. By default,
Poetry uses the base version of Python 3 installed on your system, and without
further intervention the project will be installed in a virtual environment
based on that.

```text
poetry install
```

If you have other versions of Python installed on your system then you can
add virtual environments based on them using the
[environment management](https://python-poetry.org/docs/managing-environments/)
commands. (You do not need to use Pyenv to install the other Pythons; any
method will work. You can skip the Pyenv discussion.)

Once you have activated an environment, you can issue `poetry install` again
to install it in that environment. Environments are persistent, so one
installation is sufficient unless you are actually changing the dependencies
or other aspects of the installation. You may switch at will between different
environments.

