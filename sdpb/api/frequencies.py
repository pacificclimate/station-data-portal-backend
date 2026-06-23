"""
/frequencies API implementation
"""

from pycds import History
from sdpb import get_app_session
from sdpb.cache import cache_get_or_set
from sqlalchemy import distinct, select
from sdpb.util.query import add_province_filter


def collection(provinces=None):
    def producer():
        session = get_app_session()
        q = select(distinct(History.freq).label("freq"))
        q = add_province_filter(q, provinces)
        frequencies = session.execute(q).all()
        return [f.freq for f in frequencies]

    return cache_get_or_set(
        "frequencies",
        {"provinces": provinces},
        producer,
    )
