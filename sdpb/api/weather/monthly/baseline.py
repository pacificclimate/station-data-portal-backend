from sqlalchemy import func, cast, Float
from pycds import Network, Station, History, Variable, DerivedValue
from pycds.climate_baseline_helpers import pcic_climate_variable_network_name
from sdpb import get_app_session
from sdpb.util.representation import dict_from_row


def single_item_rep(item):
    """Return representation of a single network item."""
    return dict_from_row(item)


def collection_item_rep(baseline_with_station_info):
    """
    Return representation of a baseline station monthly weather collection item.
    May conceivably be different from representation of a single item.
    """
    return single_item_rep(baseline_with_station_info)


def collection_rep(baselines_with_station_info):
    """Return representation of collection."""
    return [collection_item_rep(item) for item in baselines_with_station_info]


def baseline(session, variable, month):
    """Returns list of climate baseline data.

    :param session: (sqlalchemy.orm.session.Session) database session
    :param variable: (string) requested baseline climate variable ('tmax' | 'tmin' | 'precip')
    :param month: (int) requested baseline month (1...12)
    :return: list
    """

    db_variable_name = {
        "tmax": "Tx_Climatology",
        "tmin": "Tn_Climatology",
        "precip": "Precip_Climatology",
    }

    values = (
        session.query(DerivedValue)
        .select_from(DerivedValue)
        .join(Variable, DerivedValue.vars_id == Variable.id)
        .join(Network, Variable.network_id == Network.id)
        .filter(Network.name == pcic_climate_variable_network_name)
        .filter(Variable.name == db_variable_name[variable])
        .filter(func.date_part("month", DerivedValue.time) == float(month))
        .subquery()
    )

    values_with_station_info = (
        session.query(
            Network.name.label("network_name"),
            Station.id.label("station_db_id"),
            Station.native_id.label("station_native_id"),
            History.id.label("history_db_id"),
            History.station_name.label("station_name"),
            cast(History.lon, Float).label("lon"),
            cast(History.lat, Float).label("lat"),
            cast(History.elevation, Float).label("elevation"),
            values.c.datum.label("datum"),
        )
        .select_from(values)
        .join(History, values.c.history_id == History.id)
        .join(Station, History.station_id == Station.id)
        .join(Network, Station.network_id == Network.id)
    )

    return values_with_station_info.all()


def collection(variable=None, month=None):
    baselines_with_station_info = baseline(get_app_session(), variable, month)
    return collection_rep(baselines_with_station_info)
