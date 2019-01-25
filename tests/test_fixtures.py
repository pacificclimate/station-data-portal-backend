# Just makin' sure all the fixtures are copacetic.

from pycds import Station


def test_stations(station_session, tst_stations):
    stations = station_session.query(Station).all()
    assert len(stations) == len(tst_stations)
