from sdpb.util import parse_date

from sdpb.api.networks import \
    get_network_item_rep, get_network_collection_rep
from sdpb.api.variables import \
    get_variable_item_rep, get_variable_collection_rep
from sdpb.api.stations import \
    get_station_collection_rep, get_station_item_rep
from sdpb.api.histories import \
    get_history_collection_rep, get_history_item_rep
from sdpb.api.observations import get_counts
from flask import request

from werkzeug.wrappers import BaseResponse as Response
from flask import abort
# from flask import Response
import json


# TODO: flask.url_for !!!!

methods = {
    'collections': {
        'networks': get_network_collection_rep,
        'variables': get_variable_collection_rep,
        'stations': get_station_collection_rep,
        'histories': get_history_collection_rep,
    },
    'collection_items': {
        'networks': get_network_item_rep,
        'variables': get_variable_item_rep,
        'stations': get_station_item_rep,
        'histories': get_history_item_rep,
    },
}

collection_methods = methods['collections']
collection_item_methods = methods['collection_items']


def dispatch_collection(session, collection, **kwargs):
    print('\n### dispatch_collection', collection, kwargs)
    print('\n### dispatch_collection', request.args)
    try:
        method = collection_methods[collection]
        result = method(session)
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


def dispatch_collection_item(session, collection, id):
    print('\n### dispatch_collection_item', collection, id)
    print('\n### dispatch_collection_item', request.args)
    try:
        method = collection_item_methods[collection]
        result = method(session, id)
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


def observation_counts(session):
    """Delegate for observation counts resource."""
    params = request.args
    start_date = parse_date(params.get('start_date', None))
    end_date = parse_date(params.get('end_date', None))
    station_ids = params.get('station_ids', None)
    station_ids = station_ids and station_ids.split(",")
    # body = request.get_json()
    # start_date = parse_date(body.get('start_date', None))
    # end_date = parse_date(body.get('end_date', None))
    # station_ids = body.get('station_ids', None)

    try:
        result = get_counts(session, start_date, end_date, station_ids)
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
