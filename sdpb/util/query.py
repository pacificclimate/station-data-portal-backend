import logging
from flask import request
from sqlalchemy import func
from itertools import groupby
from pycds import (
    Network,
    Station,
    History,
    VarsPerHistory,
    StationObservationStats,
)
from sdpb.timing import log_timing


logger = logging.getLogger("sdpb")


def set_logger_level_from_qp(a_logger):
    """Set logger level from query parameter `debug`."""
    try:
        if request.args.get("debug"):
            a_logger.setLevel(logging.DEBUG)
    except:
        pass


def get_all_histories_etc(session, provinces=None):
    with log_timing("Query all histories by station", log=logger.debug):
        q = (
            session.query(History, StationObservationStats)
            .select_from(History)
            .join(
                StationObservationStats,
                StationObservationStats.history_id == History.id,
            )
        )
        # This reduces the number of rows returned, but it's not yet clear it
        # actually reduces the query time.
        q = add_station_network_publish_filter(
            q.join(Station, History.station_id == Station.id)
        )
        q = add_province_filter(q, provinces)
        return q.all()


def get_all_histories_etc_by_station(session, provinces=None):
    all_histories_etc = get_all_histories_etc(session, provinces=provinces)
    with log_timing("Group all histories by station", log=logger.debug):
        return {
            station_id: list(histories)
            for station_id, histories in groupby(
                all_histories_etc, lambda hx_etc: hx_etc.History.station_id
            )
        }


def get_all_vars_by_hx(session, group_in_database=True):
    """
    Return a dict keyed by history id, with each value containing a list of
    variables associated with that history id.

    :param session: SQLAlchemy database session
    :param group_in_database: Boolean. Group variables by history in database
        or in this code?
    :return: dict

    Grouping in database appears to be significantly (factor of ~2) faster than
    grouping in code afterwards. Unsurprising.
    """
    set_logger_level_from_qp(logger)
    if group_in_database:
        with log_timing("Query and group all vars by hx", log=logger.debug):
            rows = (
                session.query(
                    VarsPerHistory.history_id.label("history_id"),
                    func.array_agg(VarsPerHistory.vars_id).label(
                        "variable_ids"
                    ),
                )
                .group_by(VarsPerHistory.history_id)
                .all()
            )
            return {row.history_id: row.variable_ids for row in rows}

    with log_timing("Query all vars by hx", log=logger.debug):
        all_variables = session.query(
            VarsPerHistory.history_id.label("history_id"),
            VarsPerHistory.vars_id.label("id"),
        ).all()
    with log_timing("Group all vars by hx", log=logger.debug):
        result = {
            history_id: list({v.id for v in variables})
            for history_id, variables in groupby(
                all_variables, lambda v: v.history_id
            )
        }
    return result


def add_station_network_publish_filter(q):
    """Add filtering by Network.publish via Station to a query"""
    return q.join(Network, Station.network_id == Network.id).filter(
        Network.publish == True
    )


def add_province_filter(q, provinces):
    """Add filtering by province"""
    if provinces is None:
        return q
    return q.filter(History.province.in_(provinces.split(",")))