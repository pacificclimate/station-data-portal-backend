"""This module provides approximate counts of observations per station
in a specified time period.

Counts are accurate to one-month periods; no finer time resolution is available.

Results may be restricted to a subset of stations by specifying `station_ids`.
"""

import logging
import dateutil.parser
import sqlalchemy
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import cast
from flask.logging import default_handler
from flask import request, url_for
from pycds import ObsCountPerMonthHistory, ClimoObsCount, History
from sdpb import app_db
from sdpb.util import set_logger_level_from_qp


logger = logging.getLogger(__name__)
logger.addHandler(default_handler)
logger.setLevel(logging.INFO)

session = app_db.session


def observations_counts_uri(start_date=None, end_date=None, station_ids=None):
    return url_for(
        ".sdpb_api_observations_get_counts",
        start_date=start_date,
        end_date=end_date,
        station_ids=station_ids,
    )


def get_counts(start_date=None, end_date=None, station_ids=None):
    set_logger_level_from_qp(logger)

    # Set up queries for total counts by station id
    obsCountQuery = (
        session.query(
            cast(func.sum(ObsCountPerMonthHistory.count), sqlalchemy.Integer).label(
                "total"
            ),
            History.station_id.label("station_id"),
        )
        .join(History)
        .group_by(History.station_id)
    )
    climoCountQuery = (
        session.query(
            cast(func.sum(ClimoObsCount.count), sqlalchemy.Integer).label("total"),
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
        obsCountQuery = obsCountQuery.filter(History.station_id.in_(station_ids))
        climoCountQuery = climoCountQuery.filter(History.station_id.in_(station_ids))

    # Run the queries
    obsCounts = obsCountQuery.all()
    climoCounts = climoCountQuery.all()

    return {
        "uri": observations_counts_uri(
            start_date=start_date, end_date=end_date, station_ids=station_ids
        ),
        "start_date": start_date,
        "end_date": end_date,
        "station_ids": station_ids,
        "observationCounts": {r.station_id: r.total for r in obsCounts},
        "climatologyCounts": {r.station_id: r.total for r in climoCounts},
    }
