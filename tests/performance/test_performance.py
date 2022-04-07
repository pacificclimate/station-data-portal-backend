import pytest
from sdpb.api import networks
from sdpb.timing import timing


# Use this fixture in all tests in this file.
pytestmark = pytest.mark.usefixtures("flask_app")


def test_networks():
    t = timing(networks.list)
    print(f"List networks: elapsed {t['elapsed']}")
