from pycds import Station
from sdpb.api import networks, stations
from sdpb.util.representation import date_rep
from helpers import groupby_dict
from test_histories import expected_history_rep


def test_stations_uri(flask_app):
    station = Station(id=99)
    assert stations.uri(station) == "http://test/stations/99"


def expected_station_rep(station, all_histories, all_stn_obs_stats, vars_by_hx):
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
            expected_history_rep(hx, all_stn_obs_stats, vars_by_hx)
            for hx in stn_histories
        ],
    }


def test_station_collection_hx_omit_vars(
    flask_app,
    everything_session,
    tst_networks,
    tst_stations,
    tst_histories,
    tst_stn_obs_stats,
    tst_vars_by_hx,
):
    stn_reps = sorted(stations.list(compact=False), key=lambda r: r["id"])
    expected = [
        expected_station_rep(
            station, tst_histories, tst_stn_obs_stats, tst_vars_by_hx
        )
        for station in tst_stations
        if station.network_id == tst_networks[0].id
    ]
    assert stn_reps == expected
