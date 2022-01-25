# Enable helper functions to be imported
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "helpers"))

import datetime

import pytest
import testing.postgresql

from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import DDL, CreateSchema

from alembic.config import Config
from alembic import command
import alembic.config
import alembic.command

import importlib_resources

import pycds
import pycds.alembic
from pycds import Network, Station, History, Variable, DerivedValue, Obs

from sdpb import create_app

# These global variables are set by the `app` fixture as part of its setup
# (i.e., before it yields).
# TODO: This is ugly and confusing, but possibly necessary or at least
#  expedient. It was copied from the Weather Anomaly Data Service. Look there
#  for an explanation and if possible devise a better alternative.
connexion_app = None
flask_app = None
app_db = None


@pytest.fixture(scope='session')
def schema_name():
    return pycds.get_schema_name()


@pytest.fixture(scope='session')
def database_uri():
    with testing.postgresql.Postgresql() as pg:
        yield pg.url()


@pytest.fixture(scope='session')
def alembic_script_location():
    """
    This fixture extracts the filepath to the installed pycds Alembic content.
    The filepath is typically like
    `/usr/local/lib/python3.6/dist-packages/pycds/alembic`.
    """
    source = importlib_resources.files(pycds.alembic)
    yield str(source)


# app, db, session fixtures based on http://alexmic.net/flask-sqlalchemy-pytest/

@pytest.fixture(scope='session')
def app(database_uri):
    """Session-wide test Flask application"""
    global connexion_app, flask_app, app_db
    print('#### app')
    config_override = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': database_uri,
        'SERVER_NAME': 'test',
    }
    connexion_app, flask_app, app_db = create_app(config_override)

    ctx = flask_app.app_context()
    ctx.push()

    yield flask_app

    ctx.pop()


@pytest.fixture(scope="session")
def test_client(app):
    with app.test_client() as client:
        yield client


@pytest.fixture(scope="session")
def db(app):
    """Session-wide test database"""
    # TODO: Is this necessary? It's somewhat confusing.
    print('#### db')
    # db = SQLAlchemy(app)
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

    # print('@pytest.fixture db: TEARDOWN')
    # db.engine.execute("drop extension postgis cascade")  # >>> hangs here
    # print('@pytest.fixture db: drop_all')
    # pycds.Base.metadata.drop_all(bind=db.engine)
    # pycds.weather_anomaly.Base.metadata.drop_all(bind=db.engine)


def initialize_database(engine, schema_name):
    """Initialize an empty database"""
    engine.execute('CREATE EXTENSION postgis')
    engine.execute('CREATE EXTENSION plpythonu')
    engine.execute(CreateSchema(schema_name))


def migrate_database(script_location, database_uri, revision="head"):
    """Migrate a database to a specified revision using Alembic"""
    alembic_config = alembic.config.Config()
    alembic_config.set_main_option("script_location", script_location)
    alembic_config.set_main_option("sqlalchemy.url", database_uri)
    alembic.command.upgrade(alembic_config, revision)


@pytest.fixture(scope='session')
def engine(db, schema_name, alembic_script_location, database_uri):
    """Session-wide database engine"""
    print("#### engine")
    engine = db.engine
    initialize_database(engine, schema_name)
    migrate_database(alembic_script_location, database_uri)
    yield engine

@pytest.fixture(scope='function')
def session(engine):
    print('#### session')
    # TODO: Is this necessary? It's somewhat confusing.
    session = app_db.session
    # Default search path is `"$user", public`. Need to reset that to search crmp (for our db/orm content) and
    # public (for postgis functions)
    session.execute("SET search_path TO crmp, public")
    # print('\nsearch_path', [r for r in session.execute('SHOW search_path')])
    yield session
    session.rollback()
    # session.close()


# Networks


def make_tst_network(label, publish):
    return Network(
        name="Network {}".format(label),
        long_name="Network {} long name".format(label),
        virtual="Network {} virtual".format(label),
        publish=publish,
        color="Network {} color".format(label),
    )


@pytest.fixture(scope="function")
def tst_networks():
    """Networks"""
    print("#### tst_networks")
    return [make_tst_network(label, label < "C") for label in ["A", "B", "C", "D"]]


@pytest.fixture(scope="function")
def network_session(session, tst_networks):
    print("#### network_session")
    session.add_all(tst_networks)
    session.flush()
    yield session


# Variables


def make_tst_variable(label, network):
    return Variable(
        name="Variable {}".format(label),
        unit="Variable {} unit".format(label),
        precision=99,
        standard_name="Variable {} standard_name".format(label),
        cell_method="Variable {} cell_method".format(label),
        description="Variable {} description".format(label),
        display_name="Variable {} display_name".format(label),
        short_name="Variable {} short_name".format(label),
        network=network,
    )


@pytest.fixture(scope="function")
def tst_variables(tst_networks):
    """Variables"""
    network0 = tst_networks[0]  # published
    network3 = tst_networks[3]  # not published
    return [make_tst_variable(label, network0) for label in ["W", "X"]] + [
        make_tst_variable(label, network3) for label in ["Y", "Z"]
    ]


@pytest.fixture(scope="function")
def variable_session(session, tst_variables):
    session.add_all(tst_variables)
    session.flush()
    yield session


# Stations


def make_tst_station(label, network):
    return Station(
        native_id="Stn Native ID {}".format(label),
        min_obs_time=datetime.datetime(2000, 1, 2, 3, 4, 5),
        max_obs_time=datetime.datetime(2010, 1, 2, 3, 4, 5),
        network=network,
    )


@pytest.fixture(scope="function")
def tst_stations(tst_networks):
    """Stations"""
    network0 = tst_networks[0]  # published
    network3 = tst_networks[3]  # not published
    return [make_tst_station(label, network0) for label in ["S1", "S2"]] + [
        make_tst_station(label, network3) for label in ["S3", "S4"]
    ]


@pytest.fixture(scope="function")
def station_session(session, tst_stations):
    session.add_all(tst_stations)
    session.flush()
    yield session


# Histories


def make_tst_history(label, station):
    return History(
        station_name="Station Name for Hx {}".format(label),
        lon=-123.0,
        lat=50.0,
        elevation=100,
        sdate=datetime.datetime(2000, 1, 2, 3, 4, 5),
        edate=datetime.datetime(2010, 1, 2, 3, 4, 5),
        province="Province Hx {}".format(label),
        country="Country Hx {}".format(label),
        comments="Comments Hx {}".format(label),
        freq="Freq Hx {}".format(label),
        station=station,
    )


@pytest.fixture(scope="function")
def tst_histories(tst_stations):
    """Histories"""
    station0 = tst_stations[0]
    station3 = tst_stations[3]
    return [make_tst_history(label, station0) for label in ["P", "Q"]] + [
        make_tst_history(label, station3) for label in ["R", "S"]
    ]


@pytest.fixture(scope="function")
def history_session(session, tst_histories):
    session.add_all(tst_histories)
    session.flush()
    yield session


# Observations
# TODO: Add appropriate records to VarsPerHistory, and remove xfail from test
# test_station_collection_hx_vars


def make_tst_observation(label, history, variable):
    return Obs(
        datum=99,
        history=history,
        variable=variable,
    )


@pytest.fixture(scope="function")
def tst_observations(tst_histories, tst_variables):
    """Observations"""
    history = tst_histories[0]
    variable = tst_variables[0]
    return [make_tst_observation(label, history, variable) for label in ["one", "two"]]


@pytest.fixture(scope="function")
def observation_session(session, tst_observations):
    session.add_all(tst_observations)
    session.flush()
    yield session
