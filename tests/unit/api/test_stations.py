import pprint

import pytest
from pycds import Station
from sdpb.api import stations
from helpers import omit


def test_stations_uri(flask_app):
    station = Station(id=99)
    assert stations.uri(station) == "http://test/stations/99"


@pytest.mark.parametrize("compact", [False, True])
@pytest.mark.parametrize("group_vars_in_database", [False, True])
@pytest.mark.parametrize("expand", [None, "histories"])
def test_station_collection(
    flask_app,
    everything_session,
    expected_stations_collection,
    compact,
    group_vars_in_database,
    expand,
):
    received = sorted(
        stations.collection(compact=compact, expand=expand),
        key=lambda r: r["id"],
    )
    expected = sorted(
        expected_stations_collection(compact=compact, expand=expand),
        key=lambda r: r["id"],
    )
    # print()
    # print("### received")
    # pprint.pprint(received)
    # print()
    # print("### expected")
    # pprint.pprint(expected)
    expand_histories = expand == "histories"
    assert len(received) == len(expected)
    for rec, exp in zip(received, expected):
        assert omit(exp, ["histories"]) == omit(rec, ["histories"])
        # Histories have no order imposed, so it's a bit trickier to check them.
        exp_hxs = exp["histories"]
        rec_hxs = rec["histories"]
        # Check they agree on which histories
        assert {h["id"] for h in exp_hxs} == {h["id"] for h in rec_hxs}
        # Check they agree on compact
        assert {len(h) for h in exp_hxs} == {len(h) for h in rec_hxs}
        # Check they agree on expanded
        assert all(
            (len(rh) > 1) if expand_histories else (len(rh) == 1)
            for rh in rec_hxs
        )
