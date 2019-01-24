from pycds import Network


def network_uri(network):
    return '/networks/{}'.format(network.id)


def network_collection_item_rep(network):
    """Return representation of a network collection item.
    May conceivably be different than representation of a single a network.
    """
    return {
        'id': network.id,
        'uri': network_uri(network),
        'name': network.name,
        'long_name': network.long_name,
        'virtual': network.virtual,
        'color': network.color,
    }


def network_collection_rep(networks):
    """Return representation of networks collection. """
    return [network_collection_item_rep(network) for network in networks]


def get_network_collection_rep(session):
    """Get networks from database, and return their representation."""
    networks = session.query(Network)
    return network_collection_rep(networks.all())