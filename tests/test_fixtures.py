from pycds import Station


def test_stations(station_session, tst_stations):
    stations = station_session.query(Station).all()
    assert len(stations) == len(tst_stations)

    print('\nstations from test fixture')
    for stn in tst_stations:
        print('id {id}; {native_id}'.format(**stn.__dict__))

    print('\nstations from db query')
    for stn in stations:
        print('id {id}; {native_id}'.format(**stn.__dict__))

