"""
/observations API implementation

This module provides approximate counts of observations per station
in a specified time period.

Counts are accurate to one-month periods; no finer time resolution is available.

Results may be restricted to a subset of stations by specifying `station_ids`.
"""

import logging
import sqlalchemy
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import cast
from flask import url_for
from pycds import ObsCountPerMonthHistory, ClimoObsCount, History
from sdpb import app_db
from sdpb.util.query import add_province_filter

logger = logging.getLogger("sdpb")

session = app_db.session

####
# /observations/counts
####


def observations_counts_uri(start_date=None, end_date=None, station_ids=None):
    return url_for(
        "sdpb_api_observations_get_counts",
        start_date=start_date,
        end_date=end_date,
        station_ids=station_ids,
    )


def get_counts(
    start_date=None, end_date=None, station_ids=None, provinces=None
):
    # Set up queries for total counts by station id
    obsCountQuery = (
        session.query(
            cast(
                func.sum(ObsCountPerMonthHistory.count), sqlalchemy.Integer
            ).label("total"),
            History.station_id.label("station_id"),
        )
        .join(History)
        .group_by(History.station_id)
    )
    climoCountQuery = (
        session.query(
            cast(func.sum(ClimoObsCount.count), sqlalchemy.Integer).label(
                "total"
            ),
            History.station_id.label("station_id"),
        )
        .join(History)
        .group_by(History.station_id)
    )

    # Add query filters for start date, end date, station id list.
    # Note that climo count table does not discriminate on time, therefore
    # no filters for start and end dates on that query.
    if start_date:
        obsCountQuery = obsCountQuery.filter(
            ObsCountPerMonthHistory.date_trunc >= start_date
        )
    if end_date:
        obsCountQuery = obsCountQuery.filter(
            ObsCountPerMonthHistory.date_trunc <= end_date
        )
    if station_ids:
        obsCountQuery = obsCountQuery.filter(
            History.station_id.in_(station_ids)
        )
        climoCountQuery = climoCountQuery.filter(
            History.station_id.in_(station_ids)
        )
    if provinces is not None:
        obsCountQuery = add_province_filter(obsCountQuery, provinces)
        climoCountQuery = add_province_filter(climoCountQuery, provinces)

    # Run the queries
    obsCounts = obsCountQuery.all()
    climoCounts = climoCountQuery.all()

    return {
        "uri": observations_counts_uri(
            start_date=start_date, end_date=end_date, station_ids=station_ids
        ),
        "provinces": provinces,
        "start_date": start_date,
        "end_date": end_date,
        "station_ids": station_ids,
        "observationCounts": {r.station_id: r.total for r in obsCounts},
        "climatologyCounts": {r.station_id: r.total for r in climoCounts},
    }
