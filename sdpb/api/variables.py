from pycds import Variable
from sdpb.api.networks import network_uri


def variable_uri(variable):
    return '/variables/{}'.format(variable.id)


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


def get_variable_item_rep(session, id=None):
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


def get_variable_collection_rep(session):
    """Get variables from database, and return their representation."""
    variables = session.query(Variable).order_by(Variable.id.asc()).all()
    return variable_collection_rep(variables)
