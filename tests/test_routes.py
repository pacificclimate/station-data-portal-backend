"""Tests for API routing and result processing. These tests are only of the 
routing and data handling, not of the queries to the database (the latter are 
tested in test_api.py).

It's unnecessary and undesirable to invoke the database for these tests, 
so we mock the backend query methods (e.g., `variables`) with a 
replacement function that returns a fixed, known response. This is the 
function `mock`, which can serve for all .
"""

from pytest import mark
import json
import sdpb.api


def make_mock_item(name):
    def mock_item(s, id, **kwargs):
        """Mock for sdpb.api.method collection item functions, e.g,
        sdpb.api.method['items']['networks']
        See explanation in module docstring.
        """
        if id > 10:
            raise Exception('bad')
        return {
            'collection': name,
            'id': id,
        }

    return mock_item


def make_mock_collection(name):
    def mock_collection(s, **kwargs):
        """Mock for sdpb.api.method collection functions, e.g,
        sdpb.api.method['collections']['networks']
        See explanation in module docstring.
        """
        return {
            'collection': name,
        }

    return mock_collection


def mock_all_methods(monkeypatch):
    item_methods = sdpb.api.methods['items']
    for name in item_methods:
        monkeypatch.setitem(item_methods, name, make_mock_item(name))

    collection_methods = sdpb.api.methods['collections']
    for name in collection_methods:
        monkeypatch.setitem(collection_methods, name, make_mock_collection(name))


@mark.parametrize('route, status', [
    ('/networks', 200),
    ('/networks/1', 200),
    ('/networks/999', 404),
    ('/networks/not-an-int', 404),
    ('/variables', 200),
    ('/variables/2', 200),
    ('/variables/999', 404),
    ('/variables/not-an-int', 404),
    ('/stations', 200),
    ('/stations/3', 200),
    ('/stations/999', 404),
    ('/stations/not-an-int', 404),
    ('/gronks', 404),
    ('/gronks/1', 404),
])
def test_route_validity(monkeypatch, test_client, route, status):
    mock_all_methods(monkeypatch)
    response = test_client.get(route)
    assert response.status_code == status


@mark.parametrize('collection', [
    ('networks'),
    ('variables'),
    ('stations'),
])
def test_collection_route_response_data(monkeypatch, test_client, collection):
    mock_all_methods(monkeypatch)
    route = '/{}'.format(collection)
    response = test_client.get(route)
    data = json.loads(response.data.decode('utf-8'))
    assert data == {'collection': collection}


@mark.parametrize('collection, id', [
    ('networks', 1),
    ('variables', 2),
    ('stations', 3),
])
def test_item_route_response_data(
        monkeypatch, test_client, collection, id
):
    mock_all_methods(monkeypatch)
    route = '/{}/{}'.format(collection, id)
    response = test_client.get(route)
    data = json.loads(response.data.decode('utf-8'))
    assert data == {
        'collection': collection,
        'id': id,
    }
