import dateutil.parser
import logging
from flask import request
from itertools import groupby
from pycds import History, VarsPerHistory, StationObservationStats
from sdpb.timing import log_timing


logger = logging.getLogger("sdpb")


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


def obs_stats_rep(obs_stats):
    return {
        "min_obs_time": date_rep(obs_stats.min_obs_time),
        "max_obs_time": date_rep(obs_stats.max_obs_time),
        # "obs_count": int(obs_stats.obs_count),
    }


def set_logger_level_from_qp(a_logger):
    """Set logger level from query parameter `debug`."""
    try:
        if request.args.get("debug"):
            a_logger.setLevel(logging.DEBUG)
    except:
        pass


# TODO: Move these into a different util module


def get_all_histories_etc_by_station(session):
    set_logger_level_from_qp(logger)
    # TODO: Filter by Network.publish ?
    with log_timing("Query all histories by station", log=logger.debug):
        all_histories_etc = (
            session.query(History, StationObservationStats)
            .select_from(History)
            .join(
                StationObservationStats,
                StationObservationStats.history_id == History.id,
            )
            .order_by(History.station_id.asc(), History.id)
            .all()
        )

    with log_timing("Group all histories by station", log=logger.debug):
        result = {
            station_id: list(histories)
            for station_id, histories in groupby(
                all_histories_etc, lambda hx_etc: hx_etc.History.station_id
            )
        }

    return result


def get_all_vars_by_hx(session):
    set_logger_level_from_qp(logger)
    with log_timing("Query all vars by hx", log=logger.debug):
        all_variables = (
            session.query(
                VarsPerHistory.history_id.label("history_id"),
                VarsPerHistory.vars_id.label("id"),
            )
            .order_by(VarsPerHistory.history_id.asc(), VarsPerHistory.vars_id.asc())
            .all()
        )
    with log_timing("Group all vars by hx", log=logger.debug):
        result = {
            history_id: list(variables)
            for history_id, variables in groupby(
                all_variables, lambda v: v.history_id
            )
        }
    return result
