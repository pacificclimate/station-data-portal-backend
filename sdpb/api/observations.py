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
from pycds import ObsCountPerMonthHistory, History
from sdpb.util import set_logger_level_from_qp


logger = logging.getLogger(__name__)
logger.addHandler(default_handler)
logger.setLevel(logging.INFO)


def get_counts(session, start_date, end_date, station_ids):
    set_logger_level_from_qp(logger)

    q = (
        session.query(
            cast(
                func.sum(ObsCountPerMonthHistory.count),
                sqlalchemy.Integer
            ).label('total'),
            History.station_id.label('station_id')
        )
        .join(History)
        .group_by(History.station_id)
    )
    if start_date:
        q = q.filter(ObsCountPerMonthHistory.date_trunc >= start_date)
    if end_date:
        q = q.filter(ObsCountPerMonthHistory.date_trunc <= end_date)
    if station_ids:
        q = q.filter(History.station_id.in_(station_ids))

    results = q.all()
    return {
        'start_date': start_date and start_date.isoformat(),
        'end_date': end_date and end_date.isoformat(),
        'observationCounts': {
            r.station_id: r.total for r in results
        }
    }
