import time
import logging
from flask import request, url_for
from flask.logging import default_handler
from pycds import Network, Station, History
from sdpb import db
from sdpb.api.networks import network_uri
from sdpb.api.histories import history_collection_rep, history_rep
from sdpb.util import \
    date_rep, get_all_histories_by_station, get_all_vars_by_hx, \
    set_logger_level_from_qp


logger = logging.getLogger(__name__)
logger.addHandler(default_handler)
logger.setLevel(logging.INFO)

session = db.session


def station_uri(station):
    """Return uri for a station"""
    return '/stations/{}'.format(station.id)
    # return url_for('dispatch_collection_item', collection='stations', id=station.id)


def station_rep(station, histories, all_vars_by_hx):
    """Return representation of a single station item."""
    set_logger_level_from_qp(logger)
    logger.debug('station_rep id: {}'.format(station.id))
    return {
        'id': station.id,
        'uri': station_uri(station),
        'native_id': station.native_id,
        'min_obs_time': date_rep(station.min_obs_time),
        'max_obs_time': date_rep(station.max_obs_time),
        'network_uri': network_uri(station.network),
        'histories': history_collection_rep(histories, all_vars_by_hx)
    }


def get(id=None):
    set_logger_level_from_qp(logger)
    assert id is not None
    logger.debug('get station')
    station = (
        session.query(Station)
        .select_from(Station)
        .join(Network, Station.network_id == Network.id)
        .filter(Station.id==id, Network.publish==True)
        .one()
    )
    logger.debug('station retrieved')
    histories = (
        session.query(History)
        .filter_by(station_id=id)
        .order_by(History.id)
        .all()
    )
    all_vars_by_hx = get_all_vars_by_hx(session)
    return station_rep(station, histories, all_vars_by_hx)


def station_collection_item_rep(station, histories, all_vars_by_hx):
    """Return representation of a station collection item.
    May conceivably be different than representation of a single a station.
    """
    set_logger_level_from_qp(logger)
    return station_rep(station, histories, all_vars_by_hx)


def station_collection_rep(stations, all_histories_by_station, all_variables):
    """Return representation of stations collection. """

    def histories_for(station):
        start_time = time.time()
        try:
            # result = station.histories
            result = all_histories_by_station[station.id]
            logger.debug(
                'histories_for({}) elapsed time: {}'
                    .format(station.id, time.time() - start_time)
            )
            return result
        except Exception as e:
            logger.debug(
                'Exception retrieving all_histories_by_station[{}]: {}'
                    .format(station.id, e)
            )
            return []


    set_logger_level_from_qp(logger)
    return [
        station_collection_item_rep(
            station, histories_for(station), all_variables
        )
        for station in stations
    ]


def list(stride=None, limit=None, offset=None):
    """Get stations from database, and return their representation."""
    set_logger_level_from_qp(logger)
    logger.debug('get stations')

    q = (
        session.query(Station)
        .select_from(Station)
        .join(Network, Station.network_id == Network.id)
        .filter(Network.publish==True)
        .order_by(Station.id.asc())
    )
    if stride:
        q = q.filter(Station.id % stride == 0)
    if limit:
        q = q.limit(limit)
    if offset:
        q = q.offset(offset)

    stations = q.all()
    logger.debug('stations retrieved')
    all_vars_by_hx = get_all_vars_by_hx(session)

    all_histories_by_station = get_all_histories_by_station(session)
    return station_collection_rep(stations, all_histories_by_station, all_vars_by_hx)
