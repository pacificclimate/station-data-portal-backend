from collections import namedtuple
import pytest
from pycds import Variable
from sdpb.api import networks, variables


Row = namedtuple("Row", "history_id id")


@pytest.mark.parametrize(
    "variable, expected",
    [
        (Variable(id=11), "http://test/variables/11"),
        (Row(123, 22), "http://test/variables/22"),
        (33, "http://test/variables/33"),
    ],
)
def test_variables_uri(flask_app, variable, expected):
    assert variables.uri(variable) == expected


@pytest.mark.xfail(reason="Needs an version of PyCDS that has not yet been released")
# TODO: Update test to include tags attribute
def test_variable_collection(everything_session, tst_networks, tst_variables):
    vars = sorted(variables.collection(), key=lambda r: r["id"])
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


@pytest.mark.xfail(reason="Needs an version of PyCDS that has not yet been released")
# TODO: Update test to include tags attribute
def test_variable_item(everything_session, tst_networks, tst_variables):
    for var in tst_variables:
        if var.network == tst_networks[0]:
            result = variables.single(var.id)
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
