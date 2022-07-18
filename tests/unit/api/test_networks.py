from pycds import Network
from sdpb.api import networks


def test_networks_uri(flask_app):
    network = Network(id=99)
    assert networks.uri(network) == "http://test/networks/99"


def test_network_collection(everything_session, tst_networks, tst_stations):
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
            "station_count": len(
                [stn for stn in tst_stations if stn.network_id == nw.id]
            ),
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


