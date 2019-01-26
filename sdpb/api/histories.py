from sdpb.api.variables import variable_uri
from sdpb.util import date_rep


def history_rep(history):
    """Return representation of a history"""

    variables = {obs.variable for obs in history.observations}

    return {
        'id': history.id,
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
        'variable_uris': [variable_uri(variable) for variable in variables]
    }