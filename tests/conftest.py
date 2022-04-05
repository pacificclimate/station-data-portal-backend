# Enable helper functions to be imported
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "helpers"))
sys.path.append(os.path.join(os.path.dirname(__file__), "api"))

import pytest
import pycds
from sdpb import create_app


@pytest.fixture(scope="session")
def schema_name():
    return pycds.get_schema_name()


# flask_app, app_db, session fixtures based on
# http://alexmic.net/flask-sqlalchemy-pytest/


@pytest.fixture(scope="session")
def database_uri():
    raise NotImplementedError("Fixture database_uri must be implemented")


@pytest.fixture(scope="session")
def config_override():
    raise NotImplementedError("Fixture config_override must be implemented")


@pytest.fixture(scope="session")
def app_parts(database_uri, config_override):
    yield create_app(config_override)


@pytest.fixture(scope="session")
def flask_app(app_parts):
    """Session-wide test Flask application"""
    connexion_app, flask_app, app_db = app_parts

    ctx = flask_app.app_context()
    ctx.push()

    yield flask_app

    ctx.pop()


@pytest.fixture(scope="session")
def app_db(app_parts):
    """Session-wide test application database"""
    connexion_app, flask_app, app_db = app_parts
    yield app_db

    # FIXME: Database hang on teardown
    # Problem: Ironically, attempting to tear down the database properly causes
    # the tests to hang at the the end.
    # Workaround: Not tearing down the database prevents the hang, and causes
    # no other apparent problems. A similar problem with a more elegant solution
    # is documented at
    # http://docs.sqlalchemy.org/en/latest/faq/metadata_schema.html#my-program-is-hanging-when-i-say-table-drop-metadata-drop-all
    # but the solution (to close connections before dropping tables) does not
    # work. The `session` fixture does close its connection as part of its
    # teardown. That should work, but apparently not for
    # `drop extension postgis cascade`
    #
    # Nominally, the following commented out code ought to work, but it hangs
    # at the indicated line

    # print('@pytest.fixture app_db: TEARDOWN')
    # app_db.engine.execute("drop extension postgis cascade")  # >>> hangs here
    # print('@pytest.fixture app_db: drop_all')
    # pycds.Base.metadata.drop_all(bind=app_db.engine)
    # pycds.weather_anomaly.Base.metadata.drop_all(bind=app_db.engine)


