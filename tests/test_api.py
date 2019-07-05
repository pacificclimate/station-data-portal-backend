import pytest
from pycds import Network, Variable, Station, History
from sdpb.api import networks, variables, stations, histories
from sdpb.util import date_rep, float_rep
from helpers import omit


# Networks

def test_networks_uri(app):
    network = Network(id=99)
    assert networks.uri(network) == 'http://test/networks/99'


def test_network_collection(network_session, tst_networks):
    nws = sorted(
        networks.list(),
        key=lambda r: r['id']
    )
    assert nws == [
        {
            'id': nw.id,
            'name': nw.name,
            'long_name': nw.long_name,
            'virtual': nw.virtual,
            'publish': nw.publish,
            'color': nw.color,
            'uri': networks.uri(nw),
        }
        for nw in tst_networks
    ]


def test_network_item(network_session, tst_networks):
    for nw in tst_networks:
        result = networks.get(nw.id)
        assert result ==         {
            'id': nw.id,
            'name': nw.name,
            'long_name': nw.long_name,
            'virtual': nw.virtual,
            'publish': nw.publish,
            'color': nw.color,
            'uri': networks.uri(nw),
        }


# Variables

def test_variables_uri(app):
    variable = Variable(id=99)
    assert variables.uri(variable) == 'http://test/variables/99'


def test_variable_collection(variable_session, tst_variables):
    vars = sorted(
        variables.list(),
        key=lambda r: r['id']
    )
    assert vars == [
        {
            'id': var.id,
            'uri': variables.uri(var),
            'name': var.name,
            'display_name': var.display_name,
            'short_name': var.short_name,
            'standard_name': var.standard_name,
            'cell_method': var.cell_method,
            'unit': var.unit,
            'precision': var.precision,
            'network_uri': networks.uri(var.network),
        }
        for var in tst_variables
    ]


def test_variable_item(variable_session, tst_variables):
    for var in tst_variables:
        result = variables.get(var.id)
        assert result ==         {
            'id': var.id,
            'uri': variables.uri(var),
            'name': var.name,
            'display_name': var.display_name,
            'short_name': var.short_name,
            'standard_name': var.standard_name,
            'cell_method': var.cell_method,
            'unit': var.unit,
            'precision': var.precision,
            'network_uri': networks.uri(var.network),
        }


# Histories

def test_history_uri(app):
    variable = History(id=99)
    assert histories.uri(variable) == 'http://test/histories/99'

def test_history_collection_omit_vars(history_session, tst_histories):
    hxs = sorted(
        histories.list(),
        key=lambda r: r['id']
    )
    assert list(map(lambda hx: omit(hx, ['variable_uris']), hxs)) == [
        {
            'id': hx.id,
            'uri': histories.uri(hx),
            'station_name': hx.station_name,
            'lon': float_rep(hx.lon),
            'lat': float_rep(hx.lat),
            'elevation': float_rep(hx.elevation),
            'sdate': date_rep(hx.sdate),
            'edate': date_rep(hx.edate),
            'tz_offset': hx.tz_offset,
            'province': hx.province,
            'country': hx.country,
            'freq': hx.freq,
        }
        for hx in tst_histories
    ]


# Stations

def test_stations_uri(app):
    station = Station(id=99)
    assert stations.uri(station) == 'http://test/stations/99'


def test_station_collection_omit_hx(app, observation_session, tst_stations):
    stns = sorted(
        stations.list(),
        key=lambda r: r['id']
    )
    assert list(map(lambda stn: omit(stn, ['histories']), stns)) == [
        {
            'id': stn.id,
            'uri': stations.uri(stn),
            'native_id': stn.native_id,
            'min_obs_time': date_rep(stn.min_obs_time),
            'max_obs_time': date_rep(stn.max_obs_time),
            'network_uri': networks.uri(stn.network),
        }
        for stn in tst_stations
    ]


def test_station_collection_hx_omit_vars(app, observation_session, tst_stations):
    stns = sorted(
        stations.list(),
        key=lambda r: r['id']
    )

    assert [
        [
            omit(stn_hx, ['variable_uris'])
            for stn_hx in stn['histories']
        ]
        for stn in stns
    ] == [
        [
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
                'uri': histories.uri(stn_hx)
            }
            for stn_hx in stn.histories
        ]
        for stn in tst_stations
    ]

@pytest.mark.xfail(reason='Test fixtures don\'t populate VarsPerHistory')
def test_station_collection_hx_vars(app, observation_session, tst_stations):
    stns = sorted(
        stations.list(),
        key=lambda r: r['id']
    )

    assert [
        [
            set(stn_hx['variable_uris'])
            for stn_hx in stn['histories']
        ]
        for stn in stns
    ] == [
        [
            {variables.uri(obs.variable) for obs in stn_hx.observations}
            for stn_hx in stn.histories
        ]
        for stn in tst_stations
    ]
