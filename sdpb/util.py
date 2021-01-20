import dateutil.parser
import time
import logging
from flask import request
from flask.logging import default_handler
from itertools import groupby, islice
from pycds import History, VarsPerHistory

logger = logging.getLogger(__name__)
logger.addHandler(default_handler)
logger.setLevel(logging.INFO)


def dict_from_row(row):
    """Return a dict version of a SQLAlchemy result row"""
    return dict(zip(row.keys(), row))


def dicts_from_rows(rows):
    """Return a list of dicts constructed from a list of SQLAlchemy result rows"""
    return [dict_from_row(row) for row in rows]


def date_rep(date):
    return date.isoformat() if date else None


def float_rep(x):
    return float(x) if x != None else None


def parse_date(s):
    if s is None:
        return None
    return dateutil.parser.parse(s)


def set_logger_level_from_qp(a_logger):
    """Set logger level from query parameter `debug`."""
    try:
        if request.args.get("debug"):
            a_logger.setLevel(logging.DEBUG)
    except:
        pass


# TODO: Move these into a different util module


def get_all_histories_by_station(session):
    set_logger_level_from_qp(logger)
    start_time = time.time()
    all_histories = session.query(History).order_by(History.station_id.asc()).all()
    logger.debug(
        "get_all_histories_by_station: all_histories elapsed time: {}".format(
            time.time() - start_time
        )
    )

    start_time = time.time()
    result = {
        station_id: list(histories)
        for station_id, histories in groupby(all_histories, lambda hx: hx.station_id)
    }
    logger.debug(
        "get_all_histories_by_station: grouping elapsed time: {}".format(
            time.time() - start_time
        )
    )

    return result


def get_all_vars_by_hx(session):
    set_logger_level_from_qp(logger)
    start_time = time.time()
    all_variables = (
        session.query(
            VarsPerHistory.history_id.label("history_id"),
            VarsPerHistory.vars_id.label("id"),
        )
        .order_by(
            VarsPerHistory.history_id.asc(),
            VarsPerHistory.vars_id.asc(),
        )
        .all()
    )
    logger.debug(
        "get_all_vars_by_hx: all_variables elapsed time: {}".format(
            time.time() - start_time
        )
    )

    start_time = time.time()
    result = {
        history_id: list(variables)
        for history_id, variables in groupby(all_variables, lambda v: v.history_id)
    }
    logger.debug(
        "get_all_vars_by_hx: grouping elapsed time: {}".format(time.time() - start_time)
    )

    return result
