"""
/stations{station_id}/variables API implementation

Shows the variables associated with a station. 

/stations/{station_id}/variables
shows all variables that have observations associated with this stations

/stations/{station_id}/variables/{variable_id}
shows information about one variable in the context of this station

/stations/{station_id}/variables/{variable_id}/observations
fetch data from this station's observations for this variable; 
start date and end data are provided as URL parameters
"""

import logging
import datetime
from flask import url_for
from sqlalchemy import func
from pycds import Station, History, StationObservationStats, Obs, Variable, VarsPerHistory
from sdpb import get_app_session
from sdpb.api import networks
from sdpb.api import histories
from sdpb.api import variables
from sdpb.util.representation import date_rep, is_expanded
from sdpb.util.query import (
    get_all_histories_etc_by_station,
    get_all_vars_by_hx,
    add_station_network_publish_filter,
    add_province_filter,
)
from sdpb.timing import log_timing
from sdpb.api.stations import single_item_rep

####
# /stations/{station_id}/variables/{var_id}
####


def station_variable_timespan_query(session, station_id, var_id):
    """
    Returns a query with the minimum and maximum timestamps for
    observations of this variable at this station. History-agnostic;
    the minimum and maximum might correspond to different histories
    if multiple histories record the same variable at one station.
    """

    return (
        session.query(
            func.min(VarsPerHistory.start_time).label("min_obs_time"),
            func.max(VarsPerHistory.end_time).label("max_obs_time"))
            .select_from(History)
            .join(VarsPerHistory, VarsPerHistory.history_id == History.id)
            .filter(History.station_id == station_id)
            .filter(VarsPerHistory.vars_id == var_id)
        )


def get_station_variable(station_id, var_id):
    """
    Metadata about a variable specifically in the context of a station.
    Returns the usual variable information from the /variable/{id} endpoint,
    plus start and end times for data for this variable for this station.
    """
    assert station_id is not None, "station_id must be specified"
    assert var_id is not None, "var_id must be specified"
    session = get_app_session()
    timespan = station_variable_timespan_query(session, station_id, var_id).one()

    var = variables.single(var_id)
    var["min_obs_time"] = timespan.min_obs_time
    var["max_obs_time"] = timespan.max_obs_time
    var["station_id"] = station_id
    return var


####
# /stations/{station_id}/variables/
####


def get_station_variables(station_id=None):
    assert station_id is not None
    session = get_app_session()
    q = session.query(Station).select_from(Station).filter(Station.id == station_id)
    q = add_station_network_publish_filter(q)
    station = q.one()
    station_histories_etc = (
        session.query(History, StationObservationStats)
        .select_from(History)
        .join(
            StationObservationStats,
            StationObservationStats.history_id == History.id,
        )
        .filter_by(station_id=station_id)
        .order_by(History.id)
        .all()
    )
    all_vars_by_hx = get_all_vars_by_hx(session)

    vars_by_history = single_item_rep(
        station,
        station_histories_etc,
        all_vars_by_hx,
        compact=True,
        expand="histories",
    )

    variables = [h["variable_ids"] for h in vars_by_history["histories"]]
    variables = set([v for h in variables for v in h])

    return {
        "station_id": station_id,
        "variables": [get_station_variable(station_id, v) for v in variables],
    }


####
# /stations/{station_id}/variables/{var_id}/observations
####


def observations_span_uri(station_id, var_id, start_date=None, end_date=None):
    return url_for(
        "sdpb_api_station_variables_get_observations",
        station_id=station_id,
        var_id=var_id,
        start_date=start_date,
        end_date=end_date,
    )


def obs_values_by_station_query(
    session, station_id, var_id, end_date: datetime, start_date: datetime
):
    """
    Return a query for observations over a range. The query can include filters
    for start and end date, stations of interest, and province(s) of interest.

    :param session: SQLAlchemy db session
    :param station_id: (int) Station id
    :param var_id: (int) Variable id
    :param start_date: (datetime) Start date for observation counts.
    :param end_date: (datetime) End date for observation counts.
    :return: SQLAchemy query object
    """

    # Fundamental query: Sum observation counts by month and history id over history
    # id's for each station, yielding counts per station.
    q = (
        session.query(Obs)
        .filter(Variable.id == var_id)
        .filter(History.station_id == station_id)
        .join(History)
        .join(Variable)
    )

    if start_date:
        q = q.filter(Obs.time >= func.date_trunc("day", start_date))

    if end_date:
        q = q.filter(Obs.time <= func.date_trunc("day", end_date))

    return q


def get_observations(station_id, var_id, start_date=None, end_date=None):
    """
    Return a dict containing observations for a station and variable over a range.

    if no end_date is specified, todays date will be assumed.
    if no start_date is specified, the last 26 weeks will be assumed.
    if start_date is specified, it must be within the last 26 weeks as a protection against this query being used to
    return too much data.

    :param station_id: (int) Station id
    :param var_id: (int) Variable id
    :param start_date: (datetime) Start date for observations.
    :param end_date: (datetime) End date for observations.
    :return: dict
    """
    assert station_id is not None, "station_id must be specified"
    assert var_id is not None, "var_id must be specified"

    start_date_obj = datetime.datetime.fromisoformat(start_date) if start_date else None
    end_date_obj = datetime.datetime.fromisoformat(end_date) if end_date else None

    if end_date_obj is None:
        # TODO: this could be set to the last date that the station has data for
        end_date_obj = datetime.date.today()

    if (
        start_date_obj is None
        or start_date_obj > end_date_obj
        or start_date_obj < (end_date_obj - datetime.timedelta(weeks=26))
    ):
        start_date_obj = end_date_obj - datetime.timedelta(weeks=26)

    session = get_app_session()

    obs_vals_by_station = obs_values_by_station_query(
        session,
        station_id=station_id,
        var_id=var_id,
        start_date=start_date_obj,
        end_date=end_date_obj,
    ).all()

    station = session.query(Station).filter(Station.id == station_id).one()
    variable = session.query(Variable).filter(Variable.id == var_id).one()

    return {
        "uri": observations_span_uri(
            station_id, var_id, start_date=start_date, end_date=end_date
        ),
        "start_date": start_date_obj,
        "end_date": end_date_obj,
        "station": {
            "id": station.id,
            "uri": url_for("sdpb_api_stations_single", id=station.id),
            "network_uri": networks.uri(station.network),
        },
        "variable": {
            "id": variable.id,
            "uri": url_for("sdpb_api_variables_single", id=variable.id),
            "name": variable.display_name,
            "unit": variable.unit,
        },
        "observations": [
            {"value": o.datum, "time": o.time} for o in obs_vals_by_station
        ],  # list of observations
    }

