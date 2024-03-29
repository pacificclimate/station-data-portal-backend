"""
/networks API implementation

Network item rep always contains the following keys:
- id
- uri
- name
- long_name
- virtual
- publish
- color
- station_count

Networks returned are always filtered by:
- Published (publish == True)
- Has at least one Station which has at least one History (History enables
filtering Networks by province(s))
- Matches province filter (for collection)
"""

from flask import url_for
from sqlalchemy import distinct
from sqlalchemy.sql import func
from pycds import Network, Station, History
from sdpb import get_app_session
from sdpb.util.query import add_province_filter


def uri(network):
    return url_for("sdpb_api_networks_single", id=network.id)


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
        session.query(Network, func.count(distinct(Station.id)).label("station_count"))
        .select_from(Network)
        .join(Station, Station.network_id == Network.id)
        # History join allows filtering on province
        # TODO: maybe this shouldn't be in the base query
        .join(History, History.station_id == Station.id)
        .group_by(Network.id)
        .filter(Network.publish == True)
    )


def collection(provinces=None):
    q = base_query(get_app_session())
    q = add_province_filter(q, provinces)
    q = q.order_by(Network.name.asc())
    # q = q.order_by(Network.id.asc())
    networks_etc = q.all()
    return collection_rep(networks_etc)


def single(id):
    network_etc = base_query(get_app_session()).filter(Network.id == id).one()
    return single_item_rep(network_etc)
