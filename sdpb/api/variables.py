from flask import url_for
from pycds import Network, Variable
from sdpb import get_app_session
from sdpb.api import networks


def uri(variable):
    return url_for(".sdpb_api_variables_get", id=variable.id)


def single_item_rep(variable):
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
    }


def get(id=None):
    assert id is not None
    variable = (
        get_app_session()
        .query(Variable)
        .select_from(Variable)
        .join(Network, Variable.network_id == Network.id)
        .filter(Variable.id == id, Network.publish == True)
        .one()
    )
    return single_item_rep(variable)


def collection_item_rep(variable):
    """Return representation of a variable collection item.
    May conceivably be different than representation of a single a variable item.
    """
    return single_item_rep(variable)


def collection_rep(variables):
    return [collection_item_rep(variable) for variable in variables]


def list():
    """Get variables from database, and return their representation."""
    variables = (
        get_app_session()
        .query(Variable)
        .select_from(Variable)
        .join(Network, Variable.network_id == Network.id)
        .filter(Network.publish == True)
        .order_by(Variable.id.asc())
        .all()
    )
    return collection_rep(variables)
