from pycds import Network, Variable, Station
from sdpb.api.networks import \
    network_uri, network_collection_item_rep, network_collection_rep, \
    list as get_network_collection_rep, get as get_network_item_rep
from sdpb.api.variables import \
    variable_uri, variable_collection_item_rep, variable_collection_rep, \
    list as get_variable_collection_rep, get as get_variable_item_rep
from sdpb.api.stations import \
    station_uri, station_collection_item_rep, station_collection_rep, \
    list as get_station_collection_rep

from sdpb.util import date_rep
from helpers import omit


# Networks

def test_network_uri():
    network = Network(id=99)
    assert network_uri(network) == '/networks/99'


def test_network_collection(network_session, tst_networks):
    results = sorted(
        get_network_collection_rep(network_session),
        key=lambda r: r['id']
    )
    assert len(results) == len(tst_networks)
    assert results == [
        {
            'id': nw.id,
            'name': nw.name,
            'long_name': nw.long_name,
            'virtual': nw.virtual,
            'color': nw.color,
            'uri': network_uri(nw),
        }
        for nw in tst_networks
    ]


def test_network_item(network_session, tst_networks):
    for nw in tst_networks:
        result = get_network_item_rep(network_session, nw.id)
        assert result ==         {
            'id': nw.id,
            'name': nw.name,
            'long_name': nw.long_name,
            'virtual': nw.virtual,
            'color': nw.color,
            'uri': network_uri(nw),
        }


# Variables

def test_variable_uri():
    variable = Variable(id=99)
    assert variable_uri(variable) == '/variables/99'


def test_variable_collection(variable_session, tst_variables):
    results = sorted(
        get_variable_collection_rep(variable_session),
        key=lambda r: r['id']
    )
    assert len(results) == len(tst_variables)
    assert results == [
        {
            'id': var.id,
            'uri': variable_uri(var),
            'name': var.name,
            'display_name': var.display_name,
            'short_name': var.short_name,
            'standard_name': var.standard_name,
            'cell_method': var.cell_method,
            'unit': var.unit,
            'precision': var.precision,
            'network_uri': network_uri(var.network),
        }
        for var in tst_variables
    ]


def test_variable_item(variable_session, tst_variables):
    for var in tst_variables:
        result = get_variable_item_rep(variable_session, var.id)
        assert result ==         {
            'id': var.id,
            'uri': variable_uri(var),
            'name': var.name,
            'display_name': var.display_name,
            'short_name': var.short_name,
            'standard_name': var.standard_name,
            'cell_method': var.cell_method,
            'unit': var.unit,
            'precision': var.precision,
            'network_uri': network_uri(var.network),
        }


# Stations

def test_station_uri():
    station = Station(id=99)
    assert station_uri(station) == '/stations/99'


def test_station_collection(observation_session, tst_stations):
    results = sorted(
        get_station_collection_rep(observation_session),
        key=lambda r: r['id']
    )

    assert len(results) == len(tst_stations)

    for (r, stn) in zip(results, tst_stations):
        assert omit(r, ['histories']) == \
               {
                   'id': stn.id,
                   'uri': station_uri(stn),
                   'native_id': stn.native_id,
                   'min_obs_time': date_rep(stn.min_obs_time),
                   'max_obs_time': date_rep(stn.max_obs_time),
                   'network_uri': network_uri(stn.network),
               }
        for (r_hx, stn_hx) in zip(r['histories'], stn.histories):
            assert omit(r_hx, ['variable_uris']) == \
                   {
                       'id': stn_hx.id,
                       'station_name': stn_hx.station_name,
                       'lon': stn_hx.lon,
                       'lat': stn_hx.lat,
                       'elevation': stn_hx.elevation,
                       'sdate': date_rep(stn_hx.sdate),
                       'edate': date_rep(stn_hx.edate),
                       'tz_offset': stn_hx.tz_offset,
                       'province': stn_hx.province,
                       'country': stn_hx.country,
                       'freq': stn_hx.freq,
                   }
            assert set(r_hx['variable_uris']) == \
                   {variable_uri(obs.variable) for obs in stn_hx.observations}
