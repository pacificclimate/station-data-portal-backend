import pytest
from pycds import Station
from sdpb.api import networks, stations
from sdpb.util import date_rep, float_rep
from helpers import find, groupby_dict, omit
from test_histories import expected_history_rep, history_sans_vars


def test_stations_uri(app):
    station = Station(id=99)
    assert stations.uri(station) == "http://test/stations/99"


def expected_station_rep(station, all_histories, all_stn_obs_stats):
    hxs_by_station_id = groupby_dict(all_histories, key=lambda h: h.station_id)
    try:
        stn_histories = hxs_by_station_id[station.id]
    except KeyError:
        stn_histories = []

    return {
        "id": station.id,
        "uri": stations.uri(station),
        "native_id": station.native_id,
        "min_obs_time": date_rep(station.min_obs_time),
        "max_obs_time": date_rep(station.max_obs_time),
        "network_uri": networks.uri(station.network),
        "histories": [
            expected_history_rep(hx, all_stn_obs_stats) for hx in stn_histories
        ],
    }


def test_station_collection_hx_omit_vars(
    app,
    everything_session,
    tst_networks,
    tst_stations,
    tst_histories,
    tst_stn_obs_stats,
):
    stn_reps = sorted(stations.list(), key=lambda r: r["id"])
    stn_reps_wo_vars = [
        {**stn, "histories": [history_sans_vars(hx) for hx in stn["histories"]]}
        for stn in stn_reps
    ]
    expected = [
        expected_station_rep(station, tst_histories, tst_stn_obs_stats)
        for station in tst_stations
        if station.network_id == tst_networks[0].id
    ]
    assert stn_reps_wo_vars == expected
