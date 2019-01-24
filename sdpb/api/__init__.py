from sdpb.api.networks import get_network_collection_rep
from sdpb.api.variables import get_variable_collection_rep
from sdpb.api.stations import get_station_collection_rep
from werkzeug.wrappers import BaseResponse as Response
# from flask import Response
import json


method = {
    'networks': get_network_collection_rep,
    'variables': get_variable_collection_rep,
    'stations': get_station_collection_rep,
}


def dispatch(session, collection, **kwargs):
    result = method[collection](session, **kwargs)
    return Response(
        json.dumps(result),
        content_type='application/json'
    )
