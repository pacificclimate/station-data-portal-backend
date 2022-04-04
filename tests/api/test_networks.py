import pytest
from pycds import Network
from sdpb.api import networks
from helpers import find, groupby_dict, omit


def test_networks_uri(app):
    network = Network(id=99)
    assert networks.uri(network) == "http://test/networks/99"


def test_network_collection(everything_session, tst_networks):
    nws = sorted(networks.list(), key=lambda r: r["id"])
    assert nws == [
        {
            "id": nw.id,
            "name": nw.name,
            "long_name": nw.long_name,
            "virtual": nw.virtual,
            "publish": nw.publish,
            "color": nw.color,
            "uri": networks.uri(nw),
        }
        for nw in tst_networks
        if nw.publish
    ]


def test_network_item(everything_session, tst_networks):
    for nw in tst_networks:
        if nw.publish:
            result = networks.get(nw.id)
            assert result == {
                "id": nw.id,
                "name": nw.name,
                "long_name": nw.long_name,
                "virtual": nw.virtual,
                "publish": nw.publish,
                "color": nw.color,
                "uri": networks.uri(nw),
            }


