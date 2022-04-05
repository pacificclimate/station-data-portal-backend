from sdpb.api import networks
from sdpb.timing import timing


def test_networks():
    t = timing(networks.list)
    print(f"List networks: elapsed {t['elapsed']}")
