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

from itertools import count, groupby
import datetime

import pytest
import testing.postgresql

from sqlalchemy.schema import CreateSchema
from sqlalchemy.exc import NoResultFound

from alembic.config import Config
from alembic import command
import alembic.config
import alembic.command

import pycds
from pycds import (
    Network,
    Station,
    History,
    StationObservationStats,
    Variable,
    VarsPerHistory,
    Obs,
    DerivedValue,
)
import pycds.alembic
from pycds.climate_baseline_helpers import pcic_climate_variable_network_name

from sdpb.api import networks, stations
from sdpb.util.representation import date_rep, float_rep
from helpers import groupby_dict, find


@pytest.fixture(scope="package")
def schema_name():
    return pycds.get_schema_name()


@pytest.fixture(scope="package")
def alembic_script_location():
    """
    This fixture extracts the filepath to the installed pycds Alembic content.
    The filepath is typically like
    `/usr/local/lib/python3.6/dist-packages/pycds/alembic`.
    """
    try:
        import importlib_resources

        source = importlib_resources.files(pycds.alembic)
    except ModuleNotFoundError:
        import importlib.resources

        source = importlib.resources.files(pycds.alembic)

    yield str(source)


@pytest.fixture(scope="package")
def database_uri():
    with testing.postgresql.Postgresql() as pg:
        yield pg.url()


@pytest.fixture(scope="package")
def config_override(database_uri):
    return {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": database_uri,
        "SERVER_NAME": "test",
        # "SQLALCHEMY_ECHO": True,
    }


def initialize_database(engine, schema_name):
    """Initialize an empty database"""
    # Add role required by PyCDS migrations for privileged operations.
    engine.execute(f"CREATE ROLE {pycds.get_su_role_name()} WITH SUPERUSER NOINHERIT;")
    # Add extensions required by PyCDS.
    engine.execute("CREATE EXTENSION postgis")
    engine.execute("CREATE EXTENSION plpython3u")
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


@pytest.fixture(scope="package")
def engine(app_db, schema_name, alembic_script_location, database_uri):
    """Session-wide database engine"""
    print("#### engine", database_uri)
    engine = app_db.engine
    initialize_database(engine, schema_name)
    migrate_database(alembic_script_location, database_uri)
    yield engine


# Networks
# Summary:
#   A, B: published
#   C, D: not published
#   PCIC Climate Variables - special network for climate variables

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


@pytest.fixture(scope="package")
def dummy_networks():
    """Dummy networks"""
    return [make_tst_network(label, label < "C") for label in ["A", "B", "C", "D"]]


@pytest.fixture(scope="package")
def cv_network():
    """Network for baseline climate variables; name is prescribed by pycds"""
    return Network(
        id=next(network_id),
        name=pcic_climate_variable_network_name,
        publish=False,
    )


@pytest.fixture(scope="package")
def wx_networks():
    """Networks for weather stations"""
    return [Network(id=next(network_id), name="Weather Network")]


@pytest.fixture(scope="package")
def tst_networks(dummy_networks, cv_network, wx_networks):
    """All networks"""
    return dummy_networks + [cv_network] + wx_networks


# Variables
# Summary:
#   W, X in network A (published)
#   Y, Z in network C (unpublished)
#   Tx_Climatology Tn_Climatology Precip_Climatology in network PCIC Climate Variables

variable_id = count()


def make_tst_variable(label, network, **overrides):
    defaults = dict(
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
    return Variable(**{**defaults, **overrides})


@pytest.fixture(scope="package")
def dummy_variables(tst_networks):
    """Variables"""
    network0 = tst_networks[0]  # published
    network3 = tst_networks[3]  # not published
    return [make_tst_variable(label, network0) for label in ["W", "X"]] + [
        make_tst_variable(label, network3) for label in ["Y", "Z"]
    ]


@pytest.fixture(scope="package")
def cv_variables(cv_network):
    """Baseline climate variables in the climate network"""
    return [
        make_tst_variable("CV", cv_network, name=name)
        for name in "Tx_Climatology Tn_Climatology Precip_Climatology".split()
    ]


@pytest.fixture(scope="package")
def air_temp_variables(wx_networks):
    """Variables for air temperature observations in the weather (station) networks"""
    return [
        make_tst_variable(
            label="AT",
            network=network,
            name="{} air temp".format(network.name),
            standard_name="air_temperature",
            cell_method="time: point",
        )
        for network in wx_networks
    ]


@pytest.fixture(scope="package")
def precip_variables(wx_networks):
    """
    Variables for precipitation observations in the weather (station) networks.
    Returns two sets of variables per network: lwe precipitation and snowfall thickness.
    Both types are processed by MonthlyTotalPrecipitation, but only lwe should be
    returned by the weather API.
    """
    return [
        make_tst_variable(
            label="PR",
            network=network,
            name="{} lwe precip".format(network.name),
            standard_name="lwe_thickness_of_precipitation_amount",
            cell_method="time: sum",
        )
        for network in wx_networks
    ] + [
        make_tst_variable(
            label="PR",
            network=network,
            name="{} snowfall".format(network.name),
            standard_name="thickness_of_snowfall_amount",
            cell_method="time: sum",
        )
        for network in wx_networks
    ]


# Constants for weather value fixtures
year = 2000
month = 1
days = range(1, 32)
hours = range(0, 24)


@pytest.fixture(scope="package")
def tst_variables(dummy_variables, cv_variables, air_temp_variables, precip_variables):
    """All variables"""
    return dummy_variables + cv_variables + air_temp_variables + precip_variables


# Stations
# Summary:
#   S1, S2 in network A (published)
#   S3, S4 in network C (unpublished)

station_id = count()


def make_tst_station(label, network, **overrides):
    defaults = dict(
        id=next(station_id),
        network_id=network.id,
        network=network,
        native_id="Stn Native ID {}".format(label),
        min_obs_time=datetime.datetime(2000, 1, 2, 3, 4, 5),
        max_obs_time=datetime.datetime(2001, 1, 2, 3, 4, 5),
    )
    return Station(**{**defaults, **overrides})


@pytest.fixture(scope="package")
def dummy_stations(dummy_networks):
    """Dummy stations"""
    network0 = dummy_networks[0]  # published
    network3 = dummy_networks[3]  # not published
    r = [make_tst_station(label, network0) for label in ["S1", "S2"]] + [
        make_tst_station(label, network3) for label in ["S3", "S4"]
    ]
    return r


@pytest.fixture(scope="package")
def wx_stations(wx_networks):
    """Stations, 2 for each network"""
    return [
        make_tst_station(label="WX", native_id=str(j * 10 + i), network=nw)
        for j, nw in enumerate(wx_networks)
        for i in range(2)
    ]


@pytest.fixture(scope="package")
def tst_stations(dummy_stations, wx_stations):
    """Stations"""
    return dummy_stations + wx_stations


# Histories
# Summary:
#   P, Q attached to station S1 (published)
#   R, S attached to station S3 (unpublished)

history_id = count()


def make_tst_history(label, station, **overrides):
    defaults = dict(
        id=next(history_id),
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
    return History(**{**defaults, **overrides})


@pytest.fixture(scope="package")
def dummy_histories(tst_stations):
    """Dummy histories"""
    station0 = tst_stations[0]
    station3 = tst_stations[3]
    r = [make_tst_history(label, station0) for label in ["P", "Q"]] + [
        make_tst_history(label, station3) for label in ["R", "S"]
    ]
    return r


@pytest.fixture(scope="package")
def wx_histories(wx_stations):
    """Wx Histories, one for each wx station"""
    return [
        make_tst_history(
            label="WX",
            station=station,
            station_name="Station {name}".format(name=station.native_id),
            lon=-123.0,
            lat=48.5,
            elevation=100.0 + i,
            sdate=datetime.datetime(2000, 1, 1),
            freq="1-hourly",
        )
        for i, station in enumerate(wx_stations)
    ]


@pytest.fixture(scope="package")
def tst_histories(dummy_histories, wx_histories):
    """All Histories"""
    return dummy_histories + wx_histories


# Observations
# Summary:
#   several observations for history P (published), variable W
#   several observations for history P (published), variable X
#   several observations for history R (published), variable Y
#   several observations for history R (published), variable Z

observation_id = count()


def make_tst_observation(history, variable):
    return Obs(
        id=next(observation_id),
        datum=99,
        history_id=history.id,
        vars_id=variable.id,
    )


@pytest.fixture(scope="package")
def tst_observations(tst_histories, tst_variables):
    """Observations"""
    num_obs = 2
    return [
        make_tst_observation(hx, var)
        for hx, var in (
            (tst_histories[0], tst_variables[0]),
            (tst_histories[0], tst_variables[1]),
            (tst_histories[2], tst_variables[2]),
            (tst_histories[2], tst_variables[3]),
        )
        for i in range(num_obs)
    ]


# Climate Variable values


@pytest.fixture(scope="package")
def cv_values(cv_variables, tst_histories):
    """Values for each baseline climate variable for each station for each month"""
    baseline_year = 2000
    baseline_day = 15  # fudged, but should not matter
    baseline_hour = 23
    return [
        DerivedValue(
            time=datetime.datetime(baseline_year, month, baseline_day, baseline_hour),
            datum=float(month),
            variable=variable,
            history=history,
        )
        for variable in cv_variables
        for history in tst_histories
        for month in range(1, 13)
    ]


# Station observation stats
# Summary: One bogus SOS per history


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


@pytest.fixture(scope="package")
def tst_stn_obs_stats(tst_histories):
    return [make_tst_stn_obs_stat(history) for history in tst_histories]


# Vars By History


@pytest.fixture(scope="package")
def tst_vars_by_hx(tst_observations):
    return {
        hx_id: sorted(list({obs.vars_id for obs in observations}))
        for hx_id, observations in groupby(tst_observations, lambda obs: obs.history_id)
    }


# Sessions


@pytest.fixture(scope="package")
def session(engine, app_db):
    print("#### session")
    session = app_db.session
    # Default search path is `"$user", public`. Need to reset that to search
    # crmp (for our app_db/orm content) and public (for postgis functions)
    session.execute("SET search_path TO crmp, public")
    yield session
    session.rollback()
    # session.close()


@pytest.fixture(scope="package")
def everything_session(
    session,
    tst_networks,
    tst_variables,
    tst_stations,
    tst_histories,
    tst_stn_obs_stats,
    tst_observations,
    cv_values,
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
    session.add_all(cv_values)
    session.flush()
    session.execute(VarsPerHistory.refresh())
    session.flush()
    yield session


# Expected results
#
# These fixtures return the expected results of test cases run against the test
# database as defined above. (Actually, the fixtures return functions that
# return the expected results; this allows parametrizing with less fuss than
# doing it directly through the fixture.
#
# These results (should) conform to the specification (or at least the
# abstracted behaviour) of the API.


# Expected /networks results
#
# See docstring in sdpb/api/networks.py for definition behaviour.
#
# Published networks are labelled A and B.
# Stations attached to published networks are S1 and S2, both to nw A.
# Histories attached to those are P and Q, attached to S1.
# Therefore, network A is the only one that will be returned, and it has a
# station count of 1.


@pytest.fixture(scope="package")
def expected_networks_collection(tst_networks):
    def f():
        return [
            {
                "id": nw.id,
                "name": nw.name,
                "long_name": nw.long_name,
                "virtual": nw.virtual,
                "publish": nw.publish,
                "color": nw.color,
                "uri": networks.uri(nw),
                "station_count": station_count,
            }
            for nw, station_count in [(tst_networks[0], 1)]
        ]

    return f


@pytest.fixture(scope="package")
def expected_network_item_exception(tst_networks):
    def f(id_):
        if id_ == tst_networks[0].id:
            return None
        return NoResultFound

    return f


# Expected /stations results
#
# See docstring in sdpb/api/stations.py for definition behaviour.
#
# Published networks are labelled A and B.
# Stations associated to published networks are S1 and S2.
# Histories associated to those are P and Q, associated to S1.
# Therefore only station S1 should be returned.


@pytest.fixture(scope="package")
def expected_station_rep(
    tst_histories, tst_stn_obs_stats, tst_vars_by_hx, expected_history_rep
):
    def f(station, compact=False, expand=None):
        hxs_by_station_id = groupby_dict(tst_histories, key=lambda h: h.station_id)
        try:
            stn_histories = hxs_by_station_id[station.id]
        except KeyError:
            stn_histories = []

        histories_rep = [
            expected_history_rep(hx, compact=compact) for hx in stn_histories
        ]
        if "histories" not in (expand or "").split(","):
            histories_rep = [{"id": hr["id"]} for hr in histories_rep]
        rep = {
            "id": station.id,
            "uri": stations.uri(station),
            "native_id": station.native_id,
            "network_uri": networks.uri(station.network),
            "histories": histories_rep,
        }
        if compact:
            return rep
        return {
            **rep,
            "min_obs_time": date_rep(station.min_obs_time),
            "max_obs_time": date_rep(station.max_obs_time),
        }

    return f


@pytest.fixture(scope="package")
def expected_stations_collection(tst_stations, expected_station_rep):
    def f(compact, expand):
        return [
            expected_station_rep(station, compact=compact, expand=expand)
            for station in [tst_stations[0]]
        ]

    return f


# Expected /stations results
#
# See docstring in sdpb/api/histories.py for definition behaviour.
#
# Published networks are labelled A and B.
# Stations associated to published networks are S1 and S2.
# Histories associated to published stations (S1) are P and Q
# All histories have associated StationObservationStats
# Returned histories are therefore P and Q


@pytest.fixture(scope="package")
def expected_history_rep(tst_stn_obs_stats, tst_vars_by_hx):
    def f(history, compact=False):
        def history_id_match(r):
            return r.history_id == history.id

        def vars_for(history_id):
            try:
                return tst_vars_by_hx[history_id]
            except KeyError:
                return []

        rep = {
            "id": history.id,
            # "uri": histories.uri(history),
            "station_name": history.station_name,
            "lon": float_rep(history.lon),
            "lat": float_rep(history.lat),
            "elevation": float_rep(history.elevation),
            "province": history.province,
            "freq": history.freq,
            # Station obs stats
            "max_obs_time": date_rep(
                find(tst_stn_obs_stats, history_id_match).max_obs_time
            ),
            "min_obs_time": date_rep(
                find(tst_stn_obs_stats, history_id_match).min_obs_time
            ),
            "variable_ids": set(vars_for(history.id)),
            # "variable_uris": [variables.uri(v) for v in vars_for(history.id)],
        }
        if compact:
            return rep
        return {
            **rep,
            "sdate": date_rep(history.sdate),
            "edate": date_rep(history.edate),
            "tz_offset": history.tz_offset,
            "country": history.country,
        }

    return f


@pytest.fixture(scope="package")
def expected_history_collection(tst_histories, expected_history_rep):
    def f(compact):
        return [
            expected_history_rep(hx, compact=compact)
            for hx in [tst_histories[0], tst_histories[1]]
        ]

    return f
