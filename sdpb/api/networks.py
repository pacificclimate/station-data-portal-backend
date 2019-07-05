from flask import url_for
from pycds import Network
from sdpb import app_db


def network_uri(network):
    return url_for('.sdpb_api_networks_get', id=network.id)


def network_rep(network):
    """Return representation of a single network item."""
    return {
        'id': network.id,
        'uri': network_uri(network),
        'name': network.name,
        'long_name': network.long_name,
        'virtual': network.virtual,
        'publish': network.publish,
        'color': network.color,
    }


def network_collection_item_rep(network):
    """Return representation of a network collection item.
    May conceivably be different than representation of a single a network.
    """
    return network_rep(network)


def network_collection_rep(networks):
    """Return representation of networks collection. """
    return [network_collection_item_rep(network) for network in networks]


def list():
    session = app_db.session
    print('########### networks.list')
    networks = (
        session.query(Network)
            .filter_by(publish=True)
            .order_by(Network.id.asc())
            .all()
    )
    return network_collection_rep(networks)


def get(id):
    session = app_db.session
    network = session.query(Network).filter_by(id=id, publish=True).one()
    return network_rep(network)
