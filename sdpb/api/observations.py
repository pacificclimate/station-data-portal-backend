"""
/observations API implementation

This module provides approximate counts of observations per station
in a specified time period.

Counts are accurate to one-month periods; no finer time resolution is available.

Results may be restricted to a subset of stations by specifying `station_ids`.
"""

import logging
import datetime
import sqlalchemy
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import cast
from flask import url_for
from pycds import ObsCountPerMonthHistory, ClimoObsCount, History
from sdpb import get_app_session
from sdpb.util.query import add_province_filter

logger = logging.getLogger("sdpb")

####
# /observations/counts
####


def obs_counts_by_station_query(
    session, start_date=None, end_date=None, station_ids=None, provinces=None
):
    """
    Return a query for observation counts by station. The query can include filters
    for start and end date, stations of interest, and province(s) of interest.

    :param session: SQLAlchemy db session
    :param start_date: (datetime) Start date for observation counts.
    :param end_date: (datetime) End date for observation counts.
    :param station_ids: (iterable) Collection of station ids of interest.
    :param provinces: (iterable) Collection of provinces of interest.
    :return: SQLAchemy query object
    """

    # Fundamental query: Sum observation counts by month and history id over history
    # id's for each station, yielding counts per station.
    q = (
        session.query(
            cast(func.sum(ObsCountPerMonthHistory.count), sqlalchemy.Integer).label(
                "total"
            ),
            History.station_id.label("station_id"),
        )
        .join(History)
        .group_by(History.station_id)
    )

    if start_date:
        q = q.filter(
            ObsCountPerMonthHistory.date_trunc
            >= func.date_trunc("month", datetime.datetime.fromisoformat(start_date))
        )
    if end_date:
        q = q.filter(
            ObsCountPerMonthHistory.date_trunc
            <= func.date_trunc("month", datetime.datetime.fromisoformat(end_date))
        )

    if station_ids:
        q = q.filter(History.station_id.in_(station_ids))

    if provinces is not None:
        q = add_province_filter(q, provinces)

    return q


def climo_counts_by_station_query(session, station_ids=None, provinces=None):
    """
    Return a query for climatology counts by station. The query can include filters
    for stations of interest and province(s) of interest.

    :param session: SQLAlchemy db session
    :param station_ids: (iterable) Collection of station ids of interest.
    :param provinces: (iterable) Collection of provinces of interest.
    :return: SQLAchemy query object

    Climatology counts cannot be filtered by start_date and end_date; they are instead a
    sum over all dates. This is a function of how the corresponding materialized views
    in the database are defined; it cannot be changed in this code.
    """

    # Fundamental query: Sum climatology counts by history id over history
    # id's for each station, yielding counts per station.
    q = (
        session.query(
            cast(func.sum(ClimoObsCount.count), sqlalchemy.Integer).label("total"),
            History.station_id.label("station_id"),
        )
        .join(History)
        .group_by(History.station_id)
    )

    if station_ids:
        q = q.filter(History.station_id.in_(station_ids))

    if provinces is not None:
        q = add_province_filter(q, provinces)

    return q


def observations_counts_uri(start_date=None, end_date=None, station_ids=None):
    return url_for(
        "sdpb_api_observations_get_counts",
        start_date=start_date,
        end_date=end_date,
        station_ids=station_ids,
    )


def get_counts(start_date=None, end_date=None, station_ids=None, provinces=None):
    session = get_app_session()

    obs_counts_by_station = obs_counts_by_station_query(
        session,
        start_date=start_date,
        end_date=end_date,
        station_ids=station_ids,
        provinces=provinces,
    ).all()

    climo_counts_by_station = climo_counts_by_station_query(
        session, station_ids=station_ids, provinces=provinces
    ).all()

    return {
        "uri": observations_counts_uri(
            start_date=start_date, end_date=end_date, station_ids=station_ids
        ),
        "provinces": provinces,
        "start_date": start_date,
        "end_date": end_date,
        "station_ids": station_ids,
        "observationCounts": {r.station_id: r.total for r in obs_counts_by_station},
        "climatologyCounts": {r.station_id: r.total for r in climo_counts_by_station},
    }
