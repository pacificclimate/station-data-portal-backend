from pycds import Network


def network_uri(network):
    return '/networks/{}'.format(network.id)


def network_rep(network):
    """Return representation of a single network item."""
    return {
        'id': network.id,
        'uri': network_uri(network),
        'name': network.name,
        'long_name': network.long_name,
        'virtual': network.virtual,
        'color': network.color,
    }


def get_network_item_rep(session, id=None):
    assert id is not None
    network = session.query(Network).filter_by(id=id).one()
    return network_rep(network)


def network_collection_item_rep(network):
    """Return representation of a network collection item.
    May conceivably be different than representation of a single a network.
    """
    return network_rep(network)


def network_collection_rep(networks):
    """Return representation of networks collection. """
    return [network_collection_item_rep(network) for network in networks]


def get_network_collection_rep(session):
    """Get networks from database, and return their representation."""
    networks = session.query(Network).order_by(Network.id.asc()).all()
    return network_collection_rep(networks)