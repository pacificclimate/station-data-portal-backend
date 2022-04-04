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
    """Return representation of a single station item."""
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


def collection_item_rep(
    station, station_histories_etc, all_vars_by_hx=None, compact=False
):
    """Return representation of a station collection item.
    May conceivably be different than representation of a single a station.
    """
    set_logger_level_from_qp(logger)
    return single_item_rep(
        station,
        station_histories_etc,
        all_vars_by_hx=all_vars_by_hx,
        compact=compact,
    )


def collection_rep(
    stations, all_histories_etc_by_station, all_variables=None, compact=False
):
    """Return representation of stations collection."""

    def histories_etc_for(station):
        with log_timing(
            f"histories_etc_for {station.id}",
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
            all_vars_by_hx=all_variables,
            compact=compact,
        )
        for station in stations
    ]


def list(stride=None, limit=None, offset=None, compact=False):
    """Get stations from database, and return their representation."""
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
            stations = q.all()

        all_histories_etc_by_station = get_all_histories_etc_by_station(session)
        # all_vars_by_hx = None if compact else get_all_vars_by_hx(session)
        all_vars_by_hx = get_all_vars_by_hx(session)

        with log_timing("Convert stations to rep", log=logger.debug):
            return collection_rep(
                stations,
                all_histories_etc_by_station,
                all_variables=all_vars_by_hx,
                compact=compact,
            )
