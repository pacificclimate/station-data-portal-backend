import pytest
from sdpb.api.weather.monthly.weather import collection

pytestmark = pytest.mark.usefixtures("flask_app", "everything_session")


# @pytest.mark.parametrize('variable, year, month, nvm, cell_method, statistic', [
#     ('tmax', 2000, 1, 'air temp', 'time: point', 23.0),
#     ('tmin', 2000, 1, 'air temp', 'time: point', 0.0),
#     ('precip', 2000, 1, 'lwe precip', 'time: sum', float(24 * 31)),
# ])
# def test_collection(tst_histories, variable, year, month, nvm, cell_method, statistic):
#     result = collection(variable, year, month)
#     assert sorted(result, key=lambda r: r['station_name']) == \
#            [{
#                'network_name': history.station.network.name,
#                'station_db_id': history.station.id,
#                'station_native_id': history.station.native_id,
#                'history_db_id': history.id,
#                'station_name': history.station_name,
#                'lon': history.lon,
#                'lat': history.lat,
#                'elevation': history.elevation,
#                'frequency': history.freq,
#                'network_variable_name': '{} {}'.format(history.station.network.name, nvm),
#                'cell_method': cell_method,
#                'statistic': statistic,
#                'data_coverage': pytest.approx(1.0)
#            } for history in tst_histories]
