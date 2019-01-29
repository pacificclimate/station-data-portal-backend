import logging
from flask.logging import default_handler
from pycds import Station, VarsPerHistory
from sdpb.api.networks import network_uri
from sdpb.api.histories import history_collection_rep, history_rep
from sdpb.util import date_rep, get_all_vars_by_hx


logger = logging.getLogger(__name__)
logger.addHandler(default_handler)
logger.setLevel(logging.DEBUG)


def station_uri(station):
    """Return uri for a station"""
    return '/stations/{}'.format(station.id)


def station_rep(station, all_vars_by_hx):
    """Return representation of a single station item."""
    logger.debug('station_rep id: {}'.format(station.id))
    return {
        'id': station.id,
        'uri': station_uri(station),
        'native_id': station.native_id,
        'min_obs_time': date_rep(station.min_obs_time),
        'max_obs_time': date_rep(station.max_obs_time),
        'network_uri': network_uri(station.network),
        'histories': history_collection_rep(station.histories, all_vars_by_hx)
    }


def get_station_item_rep(session, id=None):
    assert id is not None
    logger.debug('get station')
    station = session.query(Station).filter_by(id=id).one()
    logger.debug('station retrieved')
    all_vars_by_hx = get_all_vars_by_hx(session)
    return station_rep(station, all_vars_by_hx)


def station_collection_item_rep(station, all_vars_by_hx):
    """Return representation of a station collection item.
    May conceivably be different than representation of a single a station.
    """
    return station_rep(station, all_vars_by_hx)


def station_collection_rep(stations, all_variables):
    """Return representation of stations collection. """
    return [station_collection_item_rep(station, all_variables) for station in stations]


def get_station_collection_rep(session):
    """Get stations from database, and return their representation."""
    logger.debug('get stations')
    stations = (
        session.query(Station)
        .order_by(Station.id.asc())
            .limit(1000)
            .all()
    )
    logger.debug('stations retrieved')
    all_vars_by_hx = get_all_vars_by_hx(session)
    return station_collection_rep(stations, all_vars_by_hx)
