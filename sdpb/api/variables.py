from flask import url_for
from pycds import Variable
from sdpb import app_db
from sdpb.api.networks import network_uri


session = app_db.session


def variable_uri(variable):
    return url_for('.sdpb_api_variables_get', id=variable.id)


def variable_rep(variable):
    """Return representation of a single variable item."""
    return {
        'id': variable.id,
        'uri': variable_uri(variable),
        'name': variable.name,
        'display_name': variable.display_name,
        'short_name': variable.short_name,
        'standard_name': variable.standard_name,
        'cell_method': variable.cell_method,
        'unit': variable.unit,
        'precision': variable.precision,
        'network_uri': network_uri(variable.network),
    }


def get(id=None):
    assert id is not None
    variable = session.query(Variable).filter_by(id=id).one()
    return variable_rep(variable)


def variable_collection_item_rep(variable):
    """Return representation of a variable collection item.
    May conceivably be different than representation of a single a variable item.
    """
    return variable_rep(variable)


def variable_collection_rep(variables):
    return [variable_collection_item_rep(variable) for variable in variables]


def list():
    """Get variables from database, and return their representation."""
    variables = session.query(Variable).order_by(Variable.id.asc()).all()
    return variable_collection_rep(variables)
