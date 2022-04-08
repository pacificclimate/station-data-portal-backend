import pytest
from sdpb.api import (
    crmp_network_geoserver,
    networks,
    variables,
    histories,
    stations,
)
from sdpb.timing import timing


# Use this fixture in all tests in this file.
pytestmark = pytest.mark.usefixtures("flask_app")


multiplier = 1000
units = "ms"


def print_timing(f, label, **kwargs):
    t = timing(
        histories.list, **kwargs
    )
    print("")
    print(
        f"{label}"
        f"({kwargs}): "
        f"{len(t['value'])} items; elapsed {t['elapsed'] * 1000} {units}"
    )


@pytest.mark.parametrize("compact", [False, True])
@pytest.mark.parametrize("group_vars_in_database", [False, True])
def test_histories_list(compact, group_vars_in_database):
    print_timing(
        histories.list,
        "histories",
        # province="BC",
        compact=compact,
        group_vars_in_database=group_vars_in_database,
    )


def test_crmp_network_geoserver():
    print_timing(crmp_network_geoserver, "crmp_network_geoserver")
