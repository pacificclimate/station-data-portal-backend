import pytest
from pycds import History
from sdpb.api import histories


def test_uri(flask_app):
    variable = History(id=99)
    assert histories.uri(variable) == "http://test/histories/99"


@pytest.mark.parametrize("compact", [False, True])
@pytest.mark.parametrize("group_vars_in_database", [True])
def test_collection(
    everything_session,
    expected_history_collection,
    compact,
    group_vars_in_database,
):
    """
    Test that the history collection includes exactly those histories for
    published stations.
    """
    result = sorted(
        histories.collection(
            compact=compact, group_vars_in_database=group_vars_in_database
        ),
        key=lambda r: r["id"],
    )
    for hx in result:
        hx["variable_ids"] = set(hx["variable_ids"])
    expected = expected_history_collection(compact)
    assert result == expected
