from flask import url_for
from pycds import Network
from sdpb import get_app_session


def uri(network):
    return url_for(".sdpb_api_networks_get", id=network.id)


def single_item_rep(network):
    """Return representation of a single network item."""
    return {
        "id": network.id,
        "uri": uri(network),
        "name": network.name,
        "long_name": network.long_name,
        "virtual": network.virtual,
        "publish": network.publish,
        "color": network.color,
    }


def collection_item_rep(network):
    """Return representation of a network collection item.
    May conceivably be different than representation of a single a network.
    """
    return single_item_rep(network)


def collection_rep(networks):
    """Return representation of networks collection."""
    return [collection_item_rep(network) for network in networks]


def list():
    networks = (
        get_app_session()
        .query(Network)
        .filter_by(publish=True)
        .order_by(Network.id.asc())
        .all()
    )
    return collection_rep(networks)


def get(id):
    network = get_app_session().query(Network).filter_by(id=id, publish=True).one()
    return single_item_rep(network)
