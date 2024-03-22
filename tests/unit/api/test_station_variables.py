import pytest
from pycds import Station
from sdpb.api import station_variables, variables, networks
from helpers import omit
from datetime import datetime



def test_station_variables(flask_app, everything_session, tst_variables):
    received = station_variables.get_station_variables(0)
    
    expected_station_variables = [0, 1]
    
    for var in expected_station_variables:
        received_var = next(v for v in received["variables"] if v["id"] == var)
        expected_var = next(v for v in tst_variables if v.id == var)
        
        assert received_var == {
                "id": expected_var.id,
                "uri": variables.uri(expected_var),
                "name": expected_var.name,
                "display_name": expected_var.display_name,
                "short_name": expected_var.short_name,
                "standard_name": expected_var.standard_name,
                "cell_method": expected_var.cell_method,
                "unit": expected_var.unit,
                "precision": expected_var.precision,
                "network_uri": networks.uri(expected_var.network),
                "tags": ['observation'],
                "min_obs_time": None,
                "max_obs_time": None,
                "station_id": 0
        }

        

def test_station_variable(flask_app, everything_session, tst_variables):
    received_var = station_variables.get_station_variable(0, 0)
    expected_var = next(v for v in tst_variables if v.id == 0)
        
    assert received_var == {
            "id": expected_var.id,
            "uri": variables.uri(expected_var),
            "name": expected_var.name,
            "display_name": expected_var.display_name,
            "short_name": expected_var.short_name,
            "standard_name": expected_var.standard_name,
            "cell_method": expected_var.cell_method,
            "unit": expected_var.unit,
            "precision": expected_var.precision,
            "network_uri": networks.uri(expected_var.network),
            "tags": ['observation'],
            "min_obs_time": None,
            "max_obs_time": None,
            "station_id": 0
        }

@pytest.mark.parametrize("station,variable,start,end,expected_obs",[
    (0, 0, datetime(2000, 1, 1), datetime(2000, 1, 31), 0),
    (0, 0, datetime(2024, 1, 1), datetime.now(), 0),
    (4, 7, datetime(1999, 1, 31), datetime(2000, 1, 31), 721),
    (4, 7, datetime(2000, 1, 15), datetime(2000, 1, 31), 385),
    (4, 0, datetime(1999, 1, 31), datetime(2000, 1, 31), 0),
    (4, 7, datetime(2024, 1, 1), datetime.now(), 0)
])
def test_station_variable_observations(
    flask_app,
    everything_session,
    expected_stations_collection,
    tst_variables,
    tst_networks,
    station,
    variable,
    start,
    end,
    expected_obs
):
    end_date = end.isoformat()
    start_date = start.isoformat()
    
    received = station_variables.get_observations(station, variable, start_date=start_date, end_date = end_date)
    assert len(received["observations"]) == expected_obs
    
