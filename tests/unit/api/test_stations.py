import pprint

import pytest
from pycds import Station
from sdpb.api import networks, stations
from sdpb.util.representation import date_rep
from helpers import groupby_dict, omit
from test_histories import expected_history_rep


def test_stations_uri(flask_app):
    station = Station(id=99)
    assert stations.uri(station) == "http://test/stations/99"


def expected_station_rep(
    station,
    all_histories,
    all_stn_obs_stats,
    vars_by_hx,
    compact=False,
    expand=None,
):
    hxs_by_station_id = groupby_dict(all_histories, key=lambda h: h.station_id)
    try:
        stn_histories = hxs_by_station_id[station.id]
    except KeyError:
        stn_histories = []

    histories_rep = [
        expected_history_rep(hx, all_stn_obs_stats, vars_by_hx, compact=compact)
        for hx in stn_histories
    ]
    if "histories" not in (expand or "").split(","):
        histories_rep = [{"uri": hr["uri"]} for hr in histories_rep]
    rep = {
        "id": station.id,
        "uri": stations.uri(station),
        "native_id": station.native_id,
        "network_uri": networks.uri(station.network),
        "histories": histories_rep,
    }
    if compact:
        return rep
    return {
        **rep,
        "min_obs_time": date_rep(station.min_obs_time),
        "max_obs_time": date_rep(station.max_obs_time),
    }


@pytest.mark.parametrize("compact", [False, True])
@pytest.mark.parametrize("group_vars_in_database", [False, True])
@pytest.mark.parametrize(
    "expand",
    [
        None,
        "histories"
    ],
)
def test_station_collection(
    flask_app,
    everything_session,
    tst_networks,
    tst_stations,
    tst_histories,
    tst_stn_obs_stats,
    tst_vars_by_hx,
    compact,
    group_vars_in_database,
    expand,
):
    received = sorted(
        stations.list(compact=compact, expand=expand), key=lambda r: r["id"]
    )
    expected = sorted(
        [
            expected_station_rep(
                station,
                tst_histories,
                tst_stn_obs_stats,
                tst_vars_by_hx,
                compact=compact,
                expand=expand,
            )
            for station in tst_stations
            if station.network.publish is True and len(station.histories) > 0
        ],
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
    for r, e in zip(received, expected):
        assert omit(e, ["histories"]) == omit(r, ["histories"])
        # Histories have no order imposed, so it's a bit trickier to check them.
        ehs = e["histories"]
        rhs = r["histories"]
        # Check they agree on which histories
        assert {h["uri"] for h in ehs} == {h["uri"] for h in rhs}
        # Check they agree on compact
        assert {len(h) for h in ehs} == {len(h) for h in rhs}
        # Check they agree on expanded
        assert all(
            (len(rh) > 1) if expand_histories else (len(rh) == 1) for rh in rhs
        )
