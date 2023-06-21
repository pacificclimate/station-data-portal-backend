from flask import url_for
from sqlalchemy import distinct, func, text
from sqlalchemy.dialects.postgresql import ARRAY, TEXT

from pycds import Network, Variable, Station, History

from sdpb import get_app_session
from sdpb.api import networks
from sdpb.util.query import add_province_filter


def id_(variable):
    """Sometimes we get a naked id, sometimes we get a database record"""
    if isinstance(variable, int):
        return variable
    # Assuming a database object with attribute id (like ORM Variable).
    return variable.id


def uri(variable):
    return url_for("sdpb_api_variables_single", id=id_(variable))


# Invoke the user-defined database function variable_tags on the Variable table.
variable_tags = func.variable_tags(text(Variable.__tablename__), type_=ARRAY(TEXT))


def single_item_rep(variable, tags):
    """Return representation of a single variable item."""
    return {
        "id": variable.id,
        "uri": uri(variable),
        "name": variable.name,
        "display_name": variable.display_name,
        "short_name": variable.short_name,
        "standard_name": variable.standard_name,
        "cell_method": variable.cell_method,
        "unit": variable.unit,
        "precision": variable.precision,
        "network_uri": networks.uri(variable.network),
        "tags": tags,
    }


def single(id=None):
    assert id is not None
    row = (
        get_app_session()
        .query(Variable, variable_tags.label("tags"))
        .select_from(Variable)
        .join(Network, Variable.network_id == Network.id)
        .filter(Variable.id == id, Network.publish == True)
        .one()
    )
    return single_item_rep(row.Variable, row.tags)


def collection_item_rep(variable, tags):
    """Return representation of a variable collection item.
    May conceivably be different from representation of a single a variable item.
    """
    return single_item_rep(variable, tags)


def collection_rep(rows):
    return [collection_item_rep(row.Variable, row.tags) for row in rows]


def collection(provinces=None):
    """Get variables from database, and return their representation."""
    session = get_app_session()

    if provinces is None:
        network_ids = session.query(Network.id.label("network_id")).select_from(Network)
    else:
        network_ids = (
            session.query(distinct(Network.id).label("network_id"))
            .select_from(Network)
            .join(Station, Station.network_id == Network.id)
            .join(History, History.station_id == Station.id)
        )
        network_ids = add_province_filter(network_ids, provinces)
    network_ids = network_ids.filter(Network.publish == True)
    network_ids = network_ids.cte(name="network_ids")

    q = (
        session.query(Variable, variable_tags.label("tags"))
        .join(network_ids, Variable.network_id == network_ids.c.network_id)
        .order_by(Variable.id.asc())
    )
    rows = q.all()
    return collection_rep(rows)
