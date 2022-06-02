from pycds import History
from sdpb import get_app_session
from sqlalchemy import distinct


def collection():
    frequencies = (
        get_app_session().query(distinct(History.freq).label("freq")).all()
    )
    return [f.freq for f in frequencies]
