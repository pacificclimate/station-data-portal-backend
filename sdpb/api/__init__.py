from sdpb.api.networks import \
    get_network_item_rep, get_network_collection_rep
from sdpb.api.variables import \
    get_variable_item_rep, get_variable_collection_rep
from sdpb.api.stations import \
    get_station_collection_rep
from werkzeug.wrappers import BaseResponse as Response
from flask import abort
# from flask import Response
import json


methods = {
    'items': {
        'networks': get_network_item_rep,
        'variables': get_variable_item_rep,
        'stations': get_station_collection_rep,
    },
    'collections': {
        'networks': get_network_collection_rep,
        'variables': get_variable_collection_rep,
        'stations': get_station_collection_rep,
    },
}


def dispatch(session, collection, **kwargs):
    # print('\n#### dispatch', collection, kwargs)
    try:
        method = methods['items' if 'id' in kwargs else 'collections'][collection]
        result = method(session, **kwargs)
        return Response(
            json.dumps(result),
            content_type='application/json'
        )
    except:
        # TODO: Need to return different status codes for different exceptions
        abort(404)
