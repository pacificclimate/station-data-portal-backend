# Enable helper functions to be imported
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'helpers'))

import datetime

from pytest import fixture
import testing.postgresql

from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import DDL, CreateSchema

import pycds
from pycds import Network, Station, History, Variable, DerivedValue, Obs

from sdpb import create_app

connexion_app = None
flask_app = None
app_db = None


# app, db, session fixtures based on http://alexmic.net/flask-sqlalchemy-pytest/

@fixture(scope='session')
def app():
    """Session-wide test Flask application"""
    global connexion_app, flask_app, app_db
    print('#### app')
    with testing.postgresql.Postgresql() as pg:
        config_override = {
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': pg.url()
        }
        connexion_app, flask_app, app_db = create_app(config_override)

        ctx = flask_app.app_context()
        ctx.push()

        yield flask_app

        ctx.pop()


@fixture(scope='session')
def test_client(app):
    with app.test_client() as client:
        yield client


@fixture(scope='session')
def db(app):
    """Session-wide test database"""
    print('#### db')
    # db = SQLAlchemy(app)
    yield app_db

    # FIXME: Database hang on teardown
    # Irony: Attempting to tear down the database properly causes the tests to hang at the the end.
    # Workaround: Not tearing down the database prevents the hang, and causes no other apparent problems.
    # A similar problem with a more elegant solution is documented at
    # http://docs.sqlalchemy.org/en/latest/faq/metadata_schema.html#my-program-is-hanging-when-i-say-table-drop-metadata-drop-all
    # but the solution (to close connections before dropping tables) does not work. The `session` fixture does close
    # its connection as part of its teardown. That should work, but apparently not for 'drop extension postgis cascade'
    #
    # Nominally, the following commented out code ought to work, but it hangs at the indicated line

    # print('@fixture db: TEARDOWN')
    # db.engine.execute("drop extension postgis cascade")  # >>> hangs here
    # print('@fixture db: drop_all')
    # pycds.Base.metadata.drop_all(bind=db.engine)
    # pycds.weather_anomaly.Base.metadata.drop_all(bind=db.engine)


@fixture(scope='session')
def engine(db):
    """Session-wide database engine"""
    print('#### engine')
    engine = db.engine
    engine.execute("create extension postgis")
    engine.execute(CreateSchema('crmp'))
    pycds.Base.metadata.create_all(bind=engine)
    yield engine

@fixture(scope='function')
def session(engine):
    """Single-test database session. All session actions are rolled back on teardown"""
    print('#### session')
    session = sessionmaker(bind=engine)()
    # Default search path is `"$user", public`. Need to reset that to search crmp (for our db/orm content) and
    # public (for postgis functions)
    session.execute('SET search_path TO crmp, public')
    # print('\nsearch_path', [r for r in session.execute('SHOW search_path')])
    yield session
    session.rollback()
    session.close()


# Networks

def make_tst_network(label):
    return Network(
        name='Network {}'.format(label),
        long_name='Network {} long name'.format(label),
        virtual='Network {} virtual'.format(label),
        publish=True,
        color='Network {} color'.format(label),
    )

@fixture(scope='function')
def tst_networks():
    """Networks"""
    print('#### tst_networks')
    return [
        make_tst_network(label) for label in ['A', 'B']
    ]

@fixture(scope='function')
def network_session(session, tst_networks):
    print('#### network_session')
    session.add_all(tst_networks)
    session.flush()
    yield session


# Variables

def make_tst_variable(label, network):
    return Variable(
        name='Variable {}'.format(label),
        unit='Variable {} unit'.format(label),
        precision=99,
        standard_name='Variable {} standard_name'.format(label),
        cell_method='Variable {} cell_method'.format(label),
        description='Variable {} description'.format(label),
        display_name='Variable {} display_name'.format(label),
        short_name='Variable {} short_name'.format(label),
        network=network,
    )

@fixture(scope='function')
def tst_variables(tst_networks):
    """Variables"""
    network = tst_networks[0]
    return [
        make_tst_variable(label, network) for label in ['X', 'Y']
    ]

@fixture(scope='function')
def variable_session(session, tst_variables):
    session.add_all(tst_variables)
    session.flush()
    yield session


# Stations

def make_tst_station(label, network):
    return Station(
        native_id='Stn Native ID {}'.format(label),
        min_obs_time=datetime.datetime(2000, 1, 2, 3, 4, 5),
        max_obs_time=datetime.datetime(2010, 1, 2, 3, 4, 5),
        network=network,
    )

@fixture(scope='function')
def tst_stations(tst_networks):
    """Stations"""
    network = tst_networks[0]
    return [
        make_tst_station(label, network) for label in ['S1', 'S2']
    ]

@fixture(scope='function')
def station_session(session, tst_stations):
    session.add_all(tst_stations)
    session.flush()
    yield session


# Histories

def make_tst_history(label, station):
    return History(
        station_name='Station Name for Hx {}'.format(label),
        lon=-123.0,
        lat=50.0,
        elevation=100,
        sdate=datetime.datetime(2000, 1, 2, 3, 4, 5),
        edate=datetime.datetime(2010, 1, 2, 3, 4, 5),
        province='Province Hx {}'.format(label),
        country='Country Hx {}'.format(label),
        comments='Comments Hx {}'.format(label),
        freq='Freq Hx {}'.format(label),
        station=station,
    )

@fixture(scope='function')
def tst_histories(tst_stations):
    """Histories"""
    station = tst_stations[0]
    return [
        make_tst_history(label, station) for label in ['P', 'Q']
    ]


# Observations

def make_tst_observation(label, history, variable):
    return Obs(
        datum=99,
        history=history,
        variable=variable,
    )


@fixture(scope='function')
def tst_observations(tst_histories, tst_variables):
    """Observations"""
    history = tst_histories[0]
    variable = tst_variables[0]
    return [
        make_tst_observation(label, history, variable) for label in ['one', 'two']
    ]


@fixture(scope='function')
def observation_session(session, tst_observations):
    session.add_all(tst_observations)
    session.flush()
    yield session
