import pytest
from pycds import Network, Variable, Station, History
from sdpb.api import networks, variables, stations, histories
from sdpb.util import date_rep, float_rep
from helpers import find, groupby_dict, omit


# Networks


def test_networks_uri(app):
    network = Network(id=99)
    assert networks.uri(network) == "http://test/networks/99"


def test_network_collection(everything_session, tst_networks):
    nws = sorted(networks.list(), key=lambda r: r["id"])
    assert nws == [
        {
            "id": nw.id,
            "name": nw.name,
            "long_name": nw.long_name,
            "virtual": nw.virtual,
            "publish": nw.publish,
            "color": nw.color,
            "uri": networks.uri(nw),
        }
        for nw in tst_networks
        if nw.publish
    ]


def test_network_item(network_session, tst_networks):
    for nw in tst_networks:
        if nw.publish:
            result = networks.get(nw.id)
            assert result == {
                "id": nw.id,
                "name": nw.name,
                "long_name": nw.long_name,
                "virtual": nw.virtual,
                "publish": nw.publish,
                "color": nw.color,
                "uri": networks.uri(nw),
            }


# Variables


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


# Histories


def test_history_uri(app):
    variable = History(id=99)
    assert histories.uri(variable) == "http://test/histories/99"


def expected_history_rep(history, all_stn_obs_stats):
    def history_id_match(r):
        return r.history_id == history.id

    return {
        "id": history.id,
        "uri": histories.uri(history),
        "station_name": history.station_name,
        "lon": float_rep(history.lon),
        "lat": float_rep(history.lat),
        "elevation": float_rep(history.elevation),
        "max_obs_time": date_rep(
            find(all_stn_obs_stats, history_id_match).max_obs_time
        ),
        "min_obs_time": date_rep(
            find(all_stn_obs_stats, history_id_match).min_obs_time
        ),
        "sdate": date_rep(history.sdate),
        "edate": date_rep(history.edate),
        "tz_offset": history.tz_offset,
        "province": history.province,
        "country": history.country,
        "freq": history.freq,
    }


def history_sans_vars(history):
    return omit(history, ["variable_uris"])


def test_history_collection_omit_vars(
    everything_session, tst_networks, tst_histories, tst_stn_obs_stats
):
    """
    Test that the history collection includes exactly those histories for
    published stations.
    ("omit_vars" refers to not checking the variables
    associated with the histories -- why are they omitted?)
    """
    result = sorted(histories.list(), key=lambda r: r["id"])
    result_wo_vars = list(map(history_sans_vars, result))
    print("### hxs", result)
    expected = [
        expected_history_rep(thx, tst_stn_obs_stats)
        for thx in tst_histories
        if thx.station.network == tst_networks[0]
    ]
    print("### expected", expected)
    assert result_wo_vars == expected


# Stations


def test_stations_uri(app):
    station = Station(id=99)
    assert stations.uri(station) == "http://test/stations/99"


def expected_station_rep(station, all_histories, all_stn_obs_stats):
    hxs_by_station_id = groupby_dict(all_histories, key=lambda h: h.station_id)
    print("### hxs_by_station_id", hxs_by_station_id)
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
    print("### stn_reps", stn_reps)

    expected = [
        expected_station_rep(station, tst_histories, tst_stn_obs_stats)
        for station in tst_stations
        if station.network_id == tst_networks[0].id
    ]
    assert stn_reps_wo_vars == expected
