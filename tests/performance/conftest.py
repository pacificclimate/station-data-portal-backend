import os
import pytest

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
