"""
stations API

A station can have a compact or full representation. A compact representation
omits some rarely-used attributes in both station proper and its associated
history items (q.v.).
"""
import logging
from flask import url_for
from sqlalchemy import func
from pycds import Network, Station, History, StationObservationStats
from sdpb import get_app_session
from sdpb.api import networks
from sdpb.api import histories
from sdpb.util.representation import date_rep
from sdpb.util.query import (
    get_all_histories_etc_by_station,
    get_all_vars_by_hx,
    set_logger_level_from_qp,
)
from sdpb.timing import log_timing


logger = logging.getLogger("sdpb")

# TODO: Name function parameters consistently


def is_expanded(item, expand):
    return expand is not None and expand == item


def uri(station):
    """Return uri for a station"""
    return url_for("sdpb_api_stations_get", id=station.id)


def single_item_rep(
    station_etc,
    station_histories_etc,
    all_vars_by_hx=None,
    compact=False,
    expand=None,
):
    """
    Return a representation of a single station item.

    :param station_etc: Database result containing a Station.
    :param station_histories_etc: Iterable containing histories etc.,
        associated with the station. For definition of histories etc.,
        see histories module.
    :param all_vars_by_hx: dict of variables associated to each history,
        keyed by history id.
    :param compact: Boolean. Return compact or full representation.
    :return: dict
    """
    """"""
    set_logger_level_from_qp(logger)
    expand_histories = is_expanded("histories", expand)

    station = getattr(station_etc, "Station", station_etc)

    if expand_histories:
        histories_rep = histories.collection_rep(
            station_histories_etc,
            all_vars_by_hx=all_vars_by_hx,
            compact=compact,
        )
    else:
        histories_rep = [
            {"uri": histories.uri(hx_id)} for hx_id in station_etc.history_ids
        ]
    rep = {
        "id": station.id,
        "uri": uri(station),
        "native_id": station.native_id,
        "network_uri": networks.uri(station.network),
        "histories": histories_rep,
    }
    if compact:
        return rep
    return {
        **rep,
        "min_obs_time": date_rep(station.min_obs_time),
        "max_obs_time": date_rep(station.max_obs_time),
    }


def collection_item_rep(
    station,
    station_histories_etc,
    all_vars_by_hx=None,
    compact=False,
    expand=None,
):
    """
    Return representation of a station collection item.
    May conceivably be different than representation of a single station.
    but at present they are the same.

    :param station: Database result containing a Station.
    :param station_histories_etc: Iterable containing histories etc.,
        associated with the station. For definition of histories etc.,
        see histories module.
    :param all_vars_by_hx: dict of variables associated to each history,
        keyed by history id.
    :param compact: Boolean. Return compact or full representation.
    :return: dict
    """
    set_logger_level_from_qp(logger)
    return single_item_rep(
        station,
        station_histories_etc,
        all_vars_by_hx=all_vars_by_hx,
        compact=compact,
        expand=expand,
    )


def collection_rep(
    stations,
    all_histories_etc_by_station,
    all_vars_by_hx=None,
    compact=False,
    expand=None,
):
    """
    Return a representation of a stations collection.

    :param stations: Iterable. Each item is a database result from a
        Station query.
    :param all_histories_etc_by_station: dict of histories etc. assocated to
        each station, keyed by station id.
    :param all_vars_by_hx: dict of variables associated to each history,
        keyed by history id.
    :param compact: Boolean. Return compact or full representation of each
        station.
    :param expand:
    :return: dict
    """

    # TODO: Consider always getting history id's in station query and doing
    #  in-code join on that basis rather than using station id and histories
    #  grouped by station. Query for histories may be faster that way.

    def histories_etc_for(station_etc):
        station = getattr(station_etc, "Station", station_etc)
        with log_timing(
            f"histories_etc_for {station.id}",
            # logging this makes the service very very slow
            # log=logger.debug,
            log=None,
        ):
            if all_histories_etc_by_station is None:
                return None
            try:
                # result = station.histories
                result = all_histories_etc_by_station[station.id]
            except KeyError:
                result = []
        return result

    set_logger_level_from_qp(logger)

    return [
        collection_item_rep(
            station,
            histories_etc_for(station),
            all_vars_by_hx=all_vars_by_hx,
            compact=compact,
            expand=expand,
        )
        for station in stations
    ]


def get(id=None):
    set_logger_level_from_qp(logger)
    assert id is not None
    session = get_app_session()
    station = (
        session.query(Station)
        .select_from(Station)
        .join(Network, Station.network_id == Network.id)
        .filter(Station.id == id, Network.publish == True)
        .one()
    )
    # TODO: Filter by Network.publish ?
    station_histories_etc = (
        session.query(History, StationObservationStats)
        .select_from(History)
        .join(
            StationObservationStats,
            StationObservationStats.history_id == History.id,
        )
        .filter_by(station_id=id)
        .order_by(History.id)
        .all()
    )
    all_vars_by_hx = get_all_vars_by_hx(session)
    return single_item_rep(station, station_histories_etc, all_vars_by_hx)


def list(
    stride=None,
    limit=None,
    offset=None,
    province=None,
    compact=True,
    group_vars_in_database=True,
    expand="histories",
):
    """
    Get stations from database, and return their representation.

    :param stride: Integer. Include only (roughly) every stride-th station.
    :param limit: Integer. Maximum number of results.
    :param offset: Integer. Offset for result set.
    :param province: String. Include only stations whose history.province
        matches this value.
    :param compact: Boolean. Return compact rep?
    :param group_vars_in_database: Boolean. Group variables by history id in
        database or in code?
    :param expand: Associated items to expand. Valid values: "histories".
    :return: list of dict
    """
    set_logger_level_from_qp(logger)
    logger.debug(
        f"stations.list(stride={stride}, limit={limit}, offset={offset}, "
        f"compact={compact}, expand={expand})"
    )
    session = get_app_session()
    expand_histories = is_expanded("histories", expand)

    with log_timing("List all stations", log=logger.debug):
        with log_timing("Query all stations", log=logger.debug):
            if expand_histories:
                q = session.query(Station).select_from(Station)
            else:
                q = session.query(
                    Station, func.array_agg(History.id).label("history_ids")
                ).group_by(Station.id)
            q = (
                q.join(Network, Station.network_id == Network.id)
                .filter(Network.publish == True)
                .order_by(Station.id.asc())
            )
            if stride:
                q = q.filter(Station.id % stride == 0)
            if limit:
                q = q.limit(limit)
            if offset:
                q = q.offset(offset)
            if province:
                q = q.join(History, History.station_id == Station.id).filter(
                    History.province == province
                )
            stations = q.all()

        all_histories_etc_by_station = (
            get_all_histories_etc_by_station(session)
            if expand_histories
            else None
        )
        all_vars_by_hx = get_all_vars_by_hx(
            session, group_in_database=group_vars_in_database
        )

        with log_timing("Convert stations to rep", log=logger.debug):
            return collection_rep(
                stations,
                all_histories_etc_by_station,
                all_vars_by_hx=all_vars_by_hx,
                compact=compact,
                expand=expand,
            )
