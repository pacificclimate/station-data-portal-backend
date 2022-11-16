import pytest
from pycds import Network
from sdpb.api import networks


def test_networks_uri(flask_app):
    network = Network(id=99)
    assert networks.uri(network) == "http://test/networks/99"


def test_network_collection(
    everything_session,
    expected_networks_collection,
):
    nws = sorted(networks.collection(), key=lambda r: r["name"])
    expected = expected_networks_collection()
    assert nws == expected


def test_network_item(
    everything_session, tst_networks, expected_network_item_exception
):
    for nw in tst_networks:
        exception = expected_network_item_exception(nw.id)
        if exception:
            with pytest.raises(exception):
                networks.single(nw.id)
        else:
            # No exception should be raised
            networks.single(nw.id)
