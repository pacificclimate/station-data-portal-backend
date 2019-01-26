from pycds import History
from sdpb.api.variables import variable_uri
from sdpb.util import date_rep


def history_uri(history):
    return '/histories/{}'.format(history.id)


def history_rep(history):
    """Return representation of a history"""

    variables = {obs.variable for obs in history.observations}

    return {
        'id': history.id,
        'uri': history_uri(history),
        'station_name': history.station_name,
        'lon': float(history.lon),
        'lat': float(history.lat),
        'elevation': float(history.elevation),
        'sdate': date_rep(history.sdate),
        'edate': date_rep(history.edate),
        'tz_offset': history.tz_offset,
        'province': history.province,
        'country': history.country,
        'freq': history.freq,
        # 'variable_uris': [variable_uri(variable) for variable in variables]
    }

def get_history_item_rep(session, id=None):
    assert id is not None
    history = session.query(History).filter_by(id=id).one()
    return history_rep(history)


def history_collection_item_rep(history):
    """Return representation of a history collection item.
    May conceivably be different than representation of a single a history.
    """
    return history_rep(history)


def history_collection_rep(historys):
    """Return representation of historys collection. """
    return [history_collection_item_rep(history) for history in historys]


def get_history_collection_rep(session):
    """Get historys from database, and return their representation."""
    historys = session.query(History).order_by(History.id.asc()).limit(10).all()
    return history_collection_rep(historys)