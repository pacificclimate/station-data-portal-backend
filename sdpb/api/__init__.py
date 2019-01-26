from sdpb.api.networks import \
    get_network_item_rep, get_network_collection_rep
from sdpb.api.variables import \
    get_variable_item_rep, get_variable_collection_rep
from sdpb.api.stations import \
    get_station_collection_rep, get_station_item_rep
from werkzeug.wrappers import BaseResponse as Response
from flask import abort
# from flask import Response
import json


methods = {
    'items': {
        'networks': get_network_item_rep,
        'variables': get_variable_item_rep,
        'stations': get_station_item_rep,
    },
    'collections': {
        'networks': get_network_collection_rep,
        'variables': get_variable_collection_rep,
        'stations': get_station_collection_rep,
    },
}


def dispatch(session, collection, **kwargs):
    print('\n### dispatch', collection, kwargs)
    try:
        method = methods['items' if 'id' in kwargs else 'collections'][collection]
        result = method(session, **kwargs)
        # print('\n### result', result)
        return Response(
            json.dumps(result),
            content_type='application/json'
        )
    except Exception as e:
        # TODO: Need to return different status codes for different exceptions
        return Response(
            json.dumps({
                'message': str(e)
            }),
            content_type='application/json'
        ), 404
