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
from pycds import \
    ObsCountPerMonthHistory, \
    ClimoObsCount, \
    History
from sdpb import app_db
from sdpb.util import set_logger_level_from_qp

import pkgutil
import sdpb
from pydap.handlers.lib import get_handler, load_handlers, parse_ce
from pydap.wsgi.app import DapServer

logger = logging.getLogger(__name__)
logger.addHandler(default_handler)
logger.setLevel(logging.INFO)

session = app_db.session


def uri(start_date=None, end_date=None, station_ids=None):
    return url_for('.sdpb_api_observations_get_counts', start_date=start_date, end_date=end_date, station_ids=station_ids)


def get_counts(start_date=None, end_date=None, station_ids=None):
    set_logger_level_from_qp(logger)

    # Set up queries for total counts by station id
    obsCountQuery = (
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
    climoCountQuery = (
        session.query(
            cast(
                func.sum(ClimoObsCount.count),
                sqlalchemy.Integer
            ).label('total'),
            History.station_id.label('station_id')
        )
        .join(History)
        .group_by(History.station_id)
    )

    # Add query filters for start date, end date, station id list.
    # Note that climo count table does not discriminate on time, therefore
    # no filters for start and end dates on that query.
    if start_date:
        obsCountQuery = (
            obsCountQuery
            .filter(ObsCountPerMonthHistory.date_trunc >= start_date)
        )
    if end_date:
        obsCountQuery = (
            obsCountQuery
            .filter(ObsCountPerMonthHistory.date_trunc <= end_date)
        )
    if station_ids:
        obsCountQuery = (
            obsCountQuery
            .filter(History.station_id.in_(station_ids))
        )
        climoCountQuery = (
            climoCountQuery
            .filter(History.station_id.in_(station_ids))
        )

    # Run the queries
    obsCounts = obsCountQuery.all()
    climoCounts = climoCountQuery.all()

    return {
        'uri': uri(start_date=start_date, end_date=end_date, station_ids=station_ids),
        'start_date': start_date,
        'end_date': end_date,
        'station_ids': station_ids,
        'observationCounts': {
            r.station_id: r.total for r in obsCounts
        },
        'climatologyCounts' : {
            r.station_id: r.total for r in climoCounts
        },
    }



pydap_app = DapServer('/home/rglover/code/station-data-portal-backend/sdpb/data')


def get_test():
    # See if we can wire up the simplest possible PyDAP response to this
    # endpoint
    # This will return a fixed file.
    # The file's type (therefore handler/reader for) is CSV.
    # The response type (therefore response/writer for) is ASCII.

    handler = get_handler('file.nc')
    print(handler)
    return 'Test'

    # filepath = pkgutil.get_data('sdpb', 'data/test.csv')
    filepath = 'data/test.csv'

    # The following would probably work if the run-time loading of packages
    # in PyDAP were simpler. But it's not.
    # handler = CSVHandler(filepath)
    # query_string = ''
    # buffer_size = 2**27
    # projection, selection = parse_ce(query_string)
    # dataset = handler.parse(projection, selection, buffer_size)
    # responder = ASCIIResponse(dataset)

    handler = get_handler(filepath)
    query_string = ''
    buffer_size = 2**27
    projection, selection = parse_ce(query_string)
    dataset = handler.parse(projection, selection, buffer_size)
    responder = handler.responses['ascii'](dataset)

    # But responder is a WSGI app; we want its guts.
    # Specifically, we want to know how a "responder" turns dataset into
    # a response.
    # I really, really, really don't want to have to establish a separate
    # service for these endpoints. Routing is the issue.
    # responder is also an __iter__
    # BUT WAIT ... https://flask.palletsprojects.com/en/1.1.x/quickstart/#about-responses
    # says that the return value from this function can be a WSGI application
    return 'Test'
    return responder


def get_timeseries_csv():
    return 'csv'

def get_timeseries_nc():
    return 'nc'

def get_timeseries_xslx():
    return 'xslx'
