from pycds import Station
from sdpb.api.networks import network_uri
from sdpb.api.histories import history_rep
from sdpb.util import date_rep


def station_uri(station):
    """Return uri for a station"""
    return '/stations/{}'.format(station.id)


def station_rep(station):
    """Return representation of a single station item."""
    return {
        'id': station.id,
        'uri': station_uri(station),
        'native_id': station.native_id,
        'min_obs_time': date_rep(station.min_obs_time),
        'max_obs_time': date_rep(station.max_obs_time),
        'network_uri': network_uri(station.network),
        'histories': [history_rep(history) for history in station.histories]
    }


def get_station_item_rep(session, id=None):
    assert id is not None
    station = session.query(Station).filter_by(id=id).one()
    return station_rep(station)


def station_collection_item_rep(station):
    """Return representation of a station collection item.
    May conceivably be different than representation of a single a station.
    """
    return station_rep(station)


def station_collection_rep(stations):
    """Return representation of stations collection. """
    return [station_collection_item_rep(station) for station in stations]


def get_station_collection_rep(session):
    """Get stations from database, and return their representation."""
    stations = session.query(Station).order_by(Station.id.asc()).all()
    return station_collection_rep(stations)
