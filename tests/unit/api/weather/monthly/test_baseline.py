import pytest
from sdpb.api.weather.monthly.baseline import collection
from helpers import hashabledictrep

pytestmark = pytest.mark.usefixtures("flask_app", "everything_session")


@pytest.mark.parametrize(
    "variable, month",
    [
        ("tmax", 1),
        ("tmin", 2),
        ("precip", 3),
    ],
)
def test_collection(tst_histories, variable, month):
    result = collection(variable, month)
    expected = [
        {
            "network_name": history.station.network.name,
            "station_db_id": history.station.id,
            "station_native_id": history.station.native_id,
            "history_db_id": history.id,
            "station_name": history.station_name,
            "lon": history.lon,
            "lat": history.lat,
            "elevation": history.elevation,
            "datum": float(month),
        }
        for history in tst_histories
    ]
    assert {hashabledictrep(r) for r in result} == {
        hashabledictrep(e) for e in expected
    }
