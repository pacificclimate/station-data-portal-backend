from sdpb.api.variables import variable_uri


def history_rep(history):
    """Return representation of a history"""

    variables = {
        variable
        for observation in history.observations
        for variable in observation.variables
    }

    return {
        'id': history.id,
        'station_name': history.station_name,
        'lon': history.lon,
        'lat': history.lat,
        'elevation': history.elevation,
        'sdate': history.sdate,
        'edate': history.edate,
        'tz_offset': history.tz_offset,
        'province': history.province,
        'country': history.country,
        'freq': history.freq,
        'variable_uris': [variable_uri(variable) for variable in variables]
    }