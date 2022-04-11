import os
import pytest

# These fixtures allow specifying the number of repeats with a command line
# option --repeats. See
# https://docs.pytest.org/en/stable/how-to/parametrize.html#basic-pytest-generate-tests-example
def pytest_addoption(parser):
    parser.addoption("--repeats", action="store", default="1")


def pytest_generate_tests(metafunc):
    # This is called for every test. Only get/set command line arguments
    # if the argument is specified in the list of test "fixturenames".
    option_value = metafunc.config.getoption("repeats")
    if 'repeats' in metafunc.fixturenames and option_value is not None:
        metafunc.parametrize("repeats", [int(option_value)])


# In this test package, we're using a real database, specified in the usual
# way by env var `PCDS_DSN`. We don't need an engine or a session because the
# app makes them for us. The app *does* need to be created and configured;
# the fixture `flask_app` does that for us. It must be used by each test in this
# package; that has to happen in the test files (apparently cannot be done in
# a conftest).


@pytest.fixture(scope="package")
def database_uri():
    return os.getenv("PCDS_DSN")


@pytest.fixture(scope="package")
def config_override(database_uri):
    return {
        # Flask errors if it doesn't have a server name. Anything will do ...
        "SERVER_NAME": "test",
    }
