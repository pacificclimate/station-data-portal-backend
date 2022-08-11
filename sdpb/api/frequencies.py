from pycds import History
from sdpb import get_app_session
from sqlalchemy import distinct
from sdpb.util.query import add_province_filter


def collection(provinces=None):
    q = get_app_session().query(distinct(History.freq).label("freq"))
    q = add_province_filter(q, provinces)
    frequencies = q.all()
    return [f.freq for f in frequencies]
