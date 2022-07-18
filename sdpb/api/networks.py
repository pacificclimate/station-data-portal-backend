from flask import url_for
from sqlalchemy.sql import func
from pycds import Network, Station
from sdpb import get_app_session


def uri(network):
    return url_for("sdpb_api_networks_get", id=network.id)


def single_item_rep(network_etc):
    """Return representation of a single network item."""
    network = network_etc.Network
    return {
        "id": network.id,
        "uri": uri(network),
        "name": network.name,
        "long_name": network.long_name,
        "virtual": network.virtual,
        "publish": network.publish,
        "color": network.color,
        "station_count": network_etc.station_count,
    }


def collection_item_rep(networks_etc):
    """Return representation of a network collection item.
    May conceivably be different than representation of a single a network.
    """
    return single_item_rep(networks_etc)


def collection_rep(networks_etc):
    """Return representation of networks collection."""
    return [collection_item_rep(network) for network in networks_etc]


def base_query(session):
    return (
        session
        .query(Network, func.count(Station.id).label("station_count"))
        .select_from(Network)
        .join(Station, Station.network_id == Network.id)
        .group_by(Network.id)
        .filter(Network.publish == True)
    )


def list():
    networks_etc = (
        base_query(get_app_session())
        .order_by(Network.id.asc())
        .all()
    )
    return collection_rep(networks_etc)


def get(id):
    network_etc = (
        base_query(get_app_session())
        .filter(Network.id == id)
        .one()
    )
    return single_item_rep(network_etc)
