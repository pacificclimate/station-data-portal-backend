import pytest
from pycds import Variable
from sdpb.api import networks, variables
from sdpb.util import date_rep, float_rep
from helpers import find, groupby_dict, omit


def test_variables_uri(app):
    variable = Variable(id=99)
    assert variables.uri(variable) == "http://test/variables/99"


def test_variable_collection(everything_session, tst_networks, tst_variables):
    vars = sorted(variables.list(), key=lambda r: r["id"])
    assert vars == [
        {
            "id": var.id,
            "uri": variables.uri(var),
            "name": var.name,
            "display_name": var.display_name,
            "short_name": var.short_name,
            "standard_name": var.standard_name,
            "cell_method": var.cell_method,
            "unit": var.unit,
            "precision": var.precision,
            "network_uri": networks.uri(var.network),
        }
        for var in tst_variables
        if var.network == tst_networks[0]
    ]


def test_variable_item(everything_session, tst_networks, tst_variables):
    for var in tst_variables:
        if var.network == tst_networks[0]:
            result = variables.get(var.id)
            assert result == {
                "id": var.id,
                "uri": variables.uri(var),
                "name": var.name,
                "display_name": var.display_name,
                "short_name": var.short_name,
                "standard_name": var.standard_name,
                "cell_method": var.cell_method,
                "unit": var.unit,
                "precision": var.precision,
                "network_uri": networks.uri(var.network),
            }


