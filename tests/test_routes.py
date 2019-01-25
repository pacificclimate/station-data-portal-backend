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


def mock(s, **kwargs):
    """Mock for sdpb.api.method functions, e.g, sdpb.api.method['networks']
    See explanation in module docstring.
    """
    return [
        {
            'foo': 'bar',
        },
    ]


def mock_all_methods(monkeypatch):
    for name in sdpb.api.method.keys():
        monkeypatch.setitem(sdpb.api.method, name, mock)


@mark.parametrize('route, status', [
    ('/networks', 200),
    ('/variables', 200),
    ('/stations', 200),
    ('/gronks', 404),
])
def test_route_validity(monkeypatch, test_client, route, status):
    mock_all_methods(monkeypatch)
    response = test_client.get(route)
    assert response.status_code == status


@mark.parametrize('route', [
    ('/networks'),
    ('/variables'),
    ('/stations'),
])
def test_route_response_data(monkeypatch, test_client, route):
    mock_all_methods(monkeypatch)
    response = test_client.get(route)
    data = json.loads(response.data.decode('utf-8'))
    assert data == [{'foo': 'bar'}]
