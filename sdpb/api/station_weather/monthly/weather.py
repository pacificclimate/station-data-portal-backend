import datetime
from sqlalchemy import cast, Float

from pycds import Network, Station, History, Variable
from pycds import (
    MonthlyAverageOfDailyMaxTemperature,
    MonthlyAverageOfDailyMinTemperature,
    MonthlyTotalPrecipitation,
)

from sdpb import get_app_session
from sdpb.util.representation import dict_from_row


def single_item_rep(item):
    """Return representation of a single network item."""
    return dict_from_row(item)


def collection_item_rep(item):
    """
    Return representation of an ongoing station monthly weather collection item.
    May conceivably be different from representation of a single item.
    """
    return single_item_rep(item)


def collection_rep(items):
    """Return representation of collection."""
    return [collection_item_rep(item) for item in items]


def weather(session, variable, year, month):
    """Returns a list of aggregated weather observations.

    :param session: (sqlalchemy.orm.session.Session) database session
    :param variable: (string) requested weather variable ('tmax' | 'tmin' | 'precip')
    :param year: (int) requested year
    :param month: (int) requested month (1...12)
    :return: (list)
    """
    view_for_variable = {
        "tmax": MonthlyAverageOfDailyMaxTemperature,
        "tmin": MonthlyAverageOfDailyMinTemperature,
        "precip": MonthlyTotalPrecipitation,
    }

    WeatherView = view_for_variable[variable]

    q = (
        session.query(
            Network.name.label("network_name"),
            Station.id.label("station_db_id"),
            Station.native_id.label("station_native_id"),
            History.id.label("history_db_id"),
            History.station_name.label("station_name"),
            cast(History.lon, Float).label("lon"),
            cast(History.lat, Float).label("lat"),
            cast(History.elevation, Float).label("elevation"),
            History.freq.label("frequency"),
            Variable.name.label("network_variable_name"),
            Variable.cell_method.label("cell_method"),
            WeatherView.statistic.label("statistic"),
            WeatherView.data_coverage.label("data_coverage"),
        )
        .select_from(WeatherView)
        .join(History, WeatherView.history_id == History.id)
        .join(History.station)
        .join(Station.network)
        .join(Variable, WeatherView.vars_id == Variable.id)
        .filter(WeatherView.obs_month == datetime.datetime(year, month, 1))
    )

    if WeatherView == MonthlyTotalPrecipitation:
        q = q.filter(Variable.standard_name == "lwe_thickness_of_precipitation_amount")

    return q.all()


def collection(variable=None, year=None, month=None):
    items = weather(get_app_session(), variable, year, month)
    return collection_rep(items)
