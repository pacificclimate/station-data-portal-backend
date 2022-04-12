import pytest
from pycds import History
from sdpb.api import histories, variables
from sdpb.util.representation import date_rep, float_rep
from helpers import find, omit


def test_uri(flask_app):
    variable = History(id=99)
    assert histories.uri(variable) == "http://test/histories/99"


def expected_history_rep(history, all_stn_obs_stats, vars_by_hx, compact=False):
    def history_id_match(r):
        return r.history_id == history.id

    def vars_for(history_id):
        try:
            return vars_by_hx[history_id]
        except KeyError:
            return []

    rep = {
        "id": history.id,
        "uri": histories.uri(history),
        "station_name": history.station_name,
        "lon": float_rep(history.lon),
        "lat": float_rep(history.lat),
        "province": history.province,
        "freq": history.freq,
        # Station obs stats
        "max_obs_time": date_rep(
            find(all_stn_obs_stats, history_id_match).max_obs_time
        ),
        "min_obs_time": date_rep(
            find(all_stn_obs_stats, history_id_match).min_obs_time
        ),
        "variable_uris": [variables.uri(v) for v in vars_for(history.id)],
    }
    if compact:
        return rep
    return {
        **rep,
        "elevation": float_rep(history.elevation),
        "sdate": date_rep(history.sdate),
        "edate": date_rep(history.edate),
        "tz_offset": history.tz_offset,
        "country": history.country,
    }


@pytest.mark.parametrize("compact", [False, True])
@pytest.mark.parametrize("group_vars_in_database", [False, True])
def test_collection(
    everything_session,
    tst_networks,
    tst_histories,
    tst_stn_obs_stats,
    tst_observations,
    tst_vars_by_hx,
    compact,
    group_vars_in_database,
):
    """
    Test that the history collection includes exactly those histories for
    published stations.
    """
    result = sorted(
        histories.list(
            compact=compact, group_vars_in_database=group_vars_in_database
        ),
        key=lambda r: r["id"],
    )
    expected = [
        expected_history_rep(
            test_hx, tst_stn_obs_stats, tst_vars_by_hx, compact=compact
        )
        for test_hx in tst_histories
        if test_hx.station.network.publish is True
    ]
    assert result == expected
