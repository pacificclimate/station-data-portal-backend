"""
stations API

A station can have a compact or full representation. A compact representation
omits some rarely-used attributes in both station proper and its associated
history items (q.v.).
"""
import logging
from flask import url_for
from pycds import Network, Station, History, StationObservationStats
from sdpb import get_app_session
from sdpb.api import networks
from sdpb.api import histories
from sdpb.util import (
    date_rep,
    get_all_histories_etc_by_station,
    get_all_vars_by_hx,
    set_logger_level_from_qp,
)
from sdpb.timing import log_timing


logger = logging.getLogger("sdpb")

# TODO: Name function parameters consistently


def uri(station):
    """Return uri for a station"""
    return url_for("sdpb_api_stations_get", id=station.id)


def single_item_rep(
    station, station_histories_etc, all_vars_by_hx=None, compact=False
):
    """
    Return a representation of a single station item.

    :param station: Database result containing a Station.
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
    rep = {
        "id": station.id,
        "uri": uri(station),
        "native_id": station.native_id,
        "network_uri": networks.uri(station.network),
        "histories": histories.collection_rep(
            station_histories_etc,
            all_vars_by_hx=all_vars_by_hx,
            compact=compact,
        ),
    }
    if compact:
        return rep
    return {
        **rep,
        "min_obs_time": date_rep(station.min_obs_time),
        "max_obs_time": date_rep(station.max_obs_time),
    }


def collection_item_rep(
    station, station_histories_etc, all_vars_by_hx=None, compact=False
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
    )


def collection_rep(
    stations, all_histories_etc_by_station, all_vars_by_hx=None, compact=False
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
    :return: dict
    """

    def histories_etc_for(station):
        with log_timing(
            f"histories_etc_for {station.id}",
            # logging this makes the service very very slow
            # log=logger.debug,
            log=None,
        ):
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
    compact=False,
    group_vars_in_database=True,
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
    :return:
    """
    set_logger_level_from_qp(logger)
    logger.debug(
        f"stations.list(stride={stride}, limit={limit}, offset={offset}, compact={compact})"
    )
    session = get_app_session()

    with log_timing("List all stations", log=logger.debug):
        with log_timing("Query all stations", log=logger.debug):
            q = (
                session.query(Station)
                .select_from(Station)
                .join(Network, Station.network_id == Network.id)
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
                q = q.join(History.station_id, Station.id).filter(offset)
            stations = q.all()

        all_histories_etc_by_station = get_all_histories_etc_by_station(session)
        all_vars_by_hx = get_all_vars_by_hx(
            session, group_in_database=group_vars_in_database
        )

        with log_timing("Convert stations to rep", log=logger.debug):
            return collection_rep(
                stations,
                all_histories_etc_by_station,
                all_vars_by_hx=all_vars_by_hx,
                compact=compact,
            )
