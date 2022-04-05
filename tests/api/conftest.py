"""
Test configuration.

Note: Primary keys in test tables are specified explicitly in setups.
This should not be necessary but it does not seem possible to build a properly
connected set of database objects without it. I believe it is forced on us
because the `pycds.StationObservationStats` lacks a relationship attribute
for history. Such relationships are apparently the basis for SQLAlchemy's
ability to link objects that have not yet been persisted to the database and
so which appear locally to have null PKs.

Adding that relationship to StationObservationStats (and any other tables
lacking the required relationship attributes) is not on the immediate path
forward. So in the meantime we do this. Ick.
"""

from itertools import count
import datetime

import pytest
import testing.postgresql

from sqlalchemy.schema import CreateSchema

from alembic.config import Config
from alembic import command
import alembic.config
import alembic.command

import importlib_resources

import pycds
from pycds import (
    Network,
    Station,
    History,
    StationObservationStats,
    Variable,
    VarsPerHistory,
    Obs,
)
import pycds.alembic


@pytest.fixture(scope="session")
def schema_name():
    return pycds.get_schema_name()


@pytest.fixture(scope="session")
def alembic_script_location():
    """
    This fixture extracts the filepath to the installed pycds Alembic content.
    The filepath is typically like
    `/usr/local/lib/python3.6/dist-packages/pycds/alembic`.
    """
    source = importlib_resources.files(pycds.alembic)
    yield str(source)


@pytest.fixture(scope="session")
def database_uri():
    with testing.postgresql.Postgresql() as pg:
        yield pg.url()


@pytest.fixture(scope="session")
def config_override(database_uri):
    return {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": database_uri,
        "SERVER_NAME": "test",
    }


def initialize_database(engine, schema_name):
    """Initialize an empty database"""
    # Add role required by PyCDS migrations for privileged operations.
    engine.execute(
        f"CREATE ROLE {pycds.get_su_role_name()} WITH SUPERUSER NOINHERIT;"
    )
    # Add extensions required by PyCDS.
    engine.execute("CREATE EXTENSION postgis")
    engine.execute("CREATE EXTENSION plpythonu")
    engine.execute("CREATE EXTENSION IF NOT EXISTS citext")
    # Add schema.
    engine.execute(CreateSchema(schema_name))


def migrate_database(script_location, database_uri, revision="head"):
    """
    Migrate a database to a specified revision using Alembic.
    This requires a privileged role to be added in advance to the database.
    """
    alembic_config = alembic.config.Config()
    alembic_config.set_main_option("script_location", script_location)
    alembic_config.set_main_option("sqlalchemy.url", database_uri)
    alembic.command.upgrade(alembic_config, revision)


@pytest.fixture(scope="session")
def engine(app_db, schema_name, alembic_script_location, database_uri):
    """Session-wide database engine"""
    print("#### engine", database_uri)
    engine = app_db.engine
    initialize_database(engine, schema_name)
    migrate_database(alembic_script_location, database_uri)
    yield engine


# Networks

network_id = count()


def make_tst_network(label, publish):
    return Network(
        id=next(network_id),
        name="Network {}".format(label),
        long_name="Network {} long name".format(label),
        virtual="Network {} virtual".format(label),
        publish=publish,
        color="Network {} color".format(label),
    )


@pytest.fixture(scope="session")
def tst_networks():
    """Networks"""
    r = [make_tst_network(label, label < "C") for label in ["A", "B", "C", "D"]]
    # print("\n### tst_networks")
    # for x in r:
    #     print(f"id={x.id} name={x.name}")
    return r


# Variables

variable_id = count()


def make_tst_variable(label, network):
    return Variable(
        id=next(variable_id),
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


@pytest.fixture(scope="session")
def tst_variables(tst_networks):
    """Variables"""
    network0 = tst_networks[0]  # published
    network3 = tst_networks[3]  # not published
    return [make_tst_variable(label, network0) for label in ["W", "X"]] + [
        make_tst_variable(label, network3) for label in ["Y", "Z"]
    ]


# Stations

station_id = count()


def make_tst_station(label, network):
    return Station(
        id=next(station_id),
        network_id=network.id,
        network=network,
        native_id="Stn Native ID {}".format(label),
        min_obs_time=datetime.datetime(2000, 1, 2, 3, 4, 5),
        max_obs_time=datetime.datetime(2001, 1, 2, 3, 4, 5),
    )


@pytest.fixture(scope="session")
def tst_stations(tst_networks):
    """Stations"""
    network0 = tst_networks[0]  # published
    network3 = tst_networks[3]  # not published
    r = [make_tst_station(label, network0) for label in ["S1", "S2"]] + [
        make_tst_station(label, network3) for label in ["S3", "S4"]
    ]
    # print("\n### tst_stations")
    # for x in r:
    #     print(f"id={x.id} network_id={x.network_id} native_id={x.native_id}")
    return r


# Histories

history_id = count()


def make_tst_history(label, station):
    return History(
        id=next(history_id),
        # station=station,
        station_id=station.id,
        station_name="Station Name for Hx {}".format(label),
        lon=-123.0,
        lat=50.0,
        elevation=100,
        sdate=datetime.datetime(2002, 1, 2, 3, 4, 5),
        edate=datetime.datetime(2003, 1, 2, 3, 4, 5),
        province="Province Hx {}".format(label),
        country="Country Hx {}".format(label),
        comments="Comments Hx {}".format(label),
        freq="Freq Hx {}".format(label),
    )


@pytest.fixture(scope="session")
def tst_histories(tst_stations):
    """Histories"""
    station0 = tst_stations[0]
    station3 = tst_stations[3]
    r = [make_tst_history(label, station0) for label in ["P", "Q"]] + [
        make_tst_history(label, station3) for label in ["R", "S"]
    ]
    # print("\n### tst_histories")
    # for x in r:
    #     print(
    #         f"id={x.id}  station_id={x.station_id}  station_name={x.station_name}"
    #     )
    return r


# Observations
# TODO: Add appropriate records to VarsPerHistory, and remove xfail from test
# test_station_collection_hx_vars

observation_id = count()


def make_tst_observation(label, history, variable):
    return Obs(
        id=next(observation_id),
        datum=99,
        history_id=history.id,
        vars_id=variable.id,
    )


@pytest.fixture(scope="session")
def tst_observations(tst_histories, tst_variables):
    """Observations"""
    history = tst_histories[0]
    variable = tst_variables[0]
    return [
        make_tst_observation(label, history, variable)
        for label in ["one", "two"]
    ]


# Station observation stats


def make_tst_stn_obs_stat(
    history,
    min_obs_time=datetime.datetime(2004, 1, 2, 3, 4, 5),
    max_obs_time=datetime.datetime(2005, 1, 2, 3, 4, 5),
    obs_count=999,
):
    return StationObservationStats(
        station_id=history.station_id,
        history_id=history.id,
        min_obs_time=min_obs_time,
        max_obs_time=max_obs_time,
        obs_count=obs_count,
    )


@pytest.fixture(scope="session")
def tst_stn_obs_stats(tst_histories):
    return [make_tst_stn_obs_stat(history) for history in tst_histories]


# Sessions


@pytest.fixture(scope="session")
def session(engine, app_db):
    print("#### session")
    session = app_db.session
    # Default search path is `"$user", public`. Need to reset that to search
    # crmp (for our app_db/orm content) and public (for postgis functions)
    session.execute("SET search_path TO crmp, public")
    # print('\nsearch_path', [r for r in session.execute('SHOW search_path')])
    yield session
    session.rollback()
    # session.close()


@pytest.fixture(scope="session")
def everything_session(
    session,
    tst_networks,
    tst_variables,
    tst_stations,
    tst_histories,
    tst_stn_obs_stats,
    tst_observations,
):
    session.add_all(tst_networks)
    session.flush()
    session.add_all(tst_variables)
    session.flush()
    session.add_all(tst_stations)
    session.flush()
    session.add_all(tst_histories)
    session.flush()
    session.add_all(tst_stn_obs_stats)
    session.flush()
    session.add_all(tst_observations)
    session.flush()
    VarsPerHistory.refresh()
    session.flush()
    yield session
