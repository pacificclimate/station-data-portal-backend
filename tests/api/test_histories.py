from pycds import History
from sdpb.api import histories
from sdpb.util.representation import date_rep, float_rep
from helpers import find, omit


def test_uri(flask_app):
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


def test_collection_omit_vars(
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
    expected = [
        expected_history_rep(thx, tst_stn_obs_stats)
        for thx in tst_histories
        if thx.station.network == tst_networks[0]
    ]
    assert result_wo_vars == expected
