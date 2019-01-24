from pycds import Station
from sdpb.api.networks import network_uri
from sdpb.api.histories import history_rep

def station_uri(station):
    """Return uri for a station"""
    return '/stations/{}'.format(station.id)


def station_collection_item_rep(station):
    """Return representation of a station collection item.
    May conceivably be different than representation of a single a station.
    """
    return {
        'id': station.id,
        'uri': station_uri(station),
        'min_obs_time': station.min_obs_time,
        'max_obs_time': station.max_obs_time,
        'native_id': station.native_id,
        'network_uri': network_uri(station.network),
        'histories': [history_rep(history) for history in station.histories]
    }


def station_collection_rep(stations):
    """Return representation of stations collection. """
    return [station_collection_item_rep(station) for station in stations]


def get_station_collection_rep(session):
    """Get stations from database, and return their representation."""
    stations = session.query(Station).order_by(Station.id.asc())
    return station_collection_rep(stations.all())
