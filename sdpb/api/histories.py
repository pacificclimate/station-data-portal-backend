import logging
from flask import url_for
from pycds import (
    History,
    VarsPerHistory,
    Network,
    Station,
    StationObservationStats,
)
from sdpb import get_app_session
from sdpb.api import variables
from sdpb.util import (
    date_rep,
    float_rep,
    get_all_vars_by_hx,
    set_logger_level_from_qp,
    obs_stats_rep,
)
from sdpb.timing import log_timing


logger = logging.getLogger("sdpb")


def uri(history):
    return url_for("sdpb_api_histories_get", id=history.id)


def single_item_rep(history_etc, vars=None, compact=False):
    """Return representation of a history"""
    history = history_etc.History
    sos = history_etc.StationObservationStats
    set_logger_level_from_qp(logger)
    rep = {
        "id": history.id,
        "uri": uri(history),
        "station_name": history.station_name,
        "lon": float_rep(history.lon),
        "lat": float_rep(history.lat),
        "province": history.province,
        "freq": history.freq,
        **obs_stats_rep(sos),
        # TODO: Why is this included for compact rep?
        "variable_uris": [variables.uri(variable) for variable in vars or []],
    }
    if compact:
        return rep
    return {
        **rep,
        "elevation": float_rep(history.elevation),
        "sdate": date_rep(history.sdate),
        "edate": date_rep(history.edate),
        "tz_offset": history.tz_offset,
        "country": history.country,
    }


def collection_item_rep(history_etc, **kwargs):
    """Return representation of a history collection item.
    May conceivably be different than representation of a single a history.
    """
    set_logger_level_from_qp(logger)
    return single_item_rep(history_etc, **kwargs)


def collection_rep(histories_etc, all_vars_by_hx=None, compact=False):
    """Return representation of historys collection."""

    def variables_for(history):
        """Return those variables connected with a specific history."""
        with log_timing(
            f"variables_for {history.id}",
            log=None,
            # log=logger.debug,
        ):
            if all_vars_by_hx is None:
                return []
            try:
                result = all_vars_by_hx[history.id]
                return result
            except KeyError as e:
                return []

    set_logger_level_from_qp(logger)

    return [
        collection_item_rep(
            history_etc,
            vars=variables_for(history_etc.History),
            compact=compact,
        )
        for history_etc in histories_etc
    ]


def get(id=None):
    """Get a single history and associated variables from database,
    and return their representation."""
    set_logger_level_from_qp(logger)
    assert id is not None
    logger.debug("get history")
    session = get_app_session()
    history_etc = (
        session.query(History, StationObservationStats)
        .select_from(History)
        .join(Station, History.station_id == Station.id)
        .join(Network, Station.network_id == Network.id)
        .join(
            StationObservationStats,
            StationObservationStats.history_id == History.id,
        )
        .filter(History.id == id, Network.publish == True)
        .one()
    )
    logger.debug("get vars")
    variables = (
        session.query(
            VarsPerHistory.history_id.label("history_id"),
            VarsPerHistory.vars_id.label("id"),
        )
        .filter(VarsPerHistory.history_id == id)
        .order_by(VarsPerHistory.vars_id)
        .all()
    )
    logger.debug("data retrieved")
    return single_item_rep(history_etc, variables)


def list(province=None, compact=False, group_vars_in_database=True):
    """
    Get histories and associated variables from database, and return their 
    representation.
        
    :param province: String. If present, return only histories whose `province`
        attribute match this value.
    :param compact: Boolean. Determines whether a compact or full/expanded
        representation is returned. A compact representation:
        - omits attributes elevation, sdate, edate, tz_offset, country
        - does not put information in attribute variables
    :param group_vars_in_database: Boolean. Perform grouping of vars by
        history id in database or in code? In db is faster.
    :return: dict
    """
    set_logger_level_from_qp(logger)
    session = get_app_session()
    with log_timing("List all histories", log=logger.debug):
        with log_timing("Query all histories etc", log=logger.debug):
            q = (
                session.query(History, StationObservationStats)
                .select_from(History)
                .join(Station, History.station_id == Station.id)
                .join(Network, Station.network_id == Network.id)
                .join(
                    StationObservationStats,
                    StationObservationStats.history_id == History.id,
                )
                .filter(Network.publish == True)
                .order_by(History.id.asc())
            )
            if province:
                q = q.filter(History.province == province)
            histories_etc = q.all()

        all_vars_by_hx = (
            None
            if compact
            else get_all_vars_by_hx(
                session, group_in_database=group_vars_in_database
            )
        )

        with log_timing("Convert histories etc to rep", log=logger.debug):
            return collection_rep(
                histories_etc, all_vars_by_hx, compact=compact
            )
