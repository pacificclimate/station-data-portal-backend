import logging
from flask import url_for
from flask.logging import default_handler
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
from sdpb.timing import timing


logger = logging.getLogger(__name__)
logger.addHandler(default_handler)
logger.setLevel(logging.DEBUG)


def uri(station):
    """Return uri for a station"""
    return url_for("sdpb_api_stations_get", id=station.id)


def single_item_rep(station, station_histories_etc, all_vars_by_hx):
    """Return representation of a single station item."""
    set_logger_level_from_qp(logger)
    logger.debug("station_rep id: {}".format(station.id))
    return {
        "id": station.id,
        "uri": uri(station),
        "native_id": station.native_id,
        "min_obs_time": date_rep(station.min_obs_time),
        "max_obs_time": date_rep(station.max_obs_time),
        "network_uri": networks.uri(station.network),
        "histories": histories.collection_rep(
            station_histories_etc, all_vars_by_hx
        ),
    }


def get(id=None):
    set_logger_level_from_qp(logger)
    assert id is not None
    logger.debug("get station")
    session = get_app_session()
    station = (
        session.query(Station)
        .select_from(Station)
        .join(Network, Station.network_id == Network.id)
        .filter(Station.id == id, Network.publish == True)
        .one()
    )
    logger.debug("station retrieved")
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


def collection_item_rep(station, station_histories_etc, all_vars_by_hx):
    """Return representation of a station collection item.
    May conceivably be different than representation of a single a station.
    """
    set_logger_level_from_qp(logger)
    return single_item_rep(station, station_histories_etc, all_vars_by_hx)


def collection_rep(stations, all_histories_etc_by_station, all_variables):
    """Return representation of stations collection."""

    def histories_etc_for(station):
        with timing("histories_etc_for", log=logger.debug):
            try:
                # result = station.histories
                result = all_histories_etc_by_station[station.id]
            except Exception as e:
                result = []
            return result

    set_logger_level_from_qp(logger)
    return [
        collection_item_rep(station, histories_etc_for(station), all_variables)
        for station in stations
    ]


def list(stride=None, limit=None, offset=None):
    """Get stations from database, and return their representation."""
    set_logger_level_from_qp(logger)
    logger.debug("get stations")
    session = get_app_session()

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
    logger.debug("stations retrieved")
    all_vars_by_hx = get_all_vars_by_hx(session)

    all_histories_etc_by_station = get_all_histories_etc_by_station(session)
    return collection_rep(
        stations, all_histories_etc_by_station, all_vars_by_hx
    )
