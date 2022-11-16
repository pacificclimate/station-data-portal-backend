import logging
from pycds import CrmpNetworkGeoserver
from sdpb import get_app_session
from sdpb.timing import log_timing


logger = logging.getLogger("sdpb")


item_keys = (
    "network_name",
    "native_id",
    "station_name",
    "lon",
    "lat",
    "elev",
    "min_obs_time",
    "max_obs_time",
    "freq",
    "tz_offset",
    "province",
    "station_id",
    "history_id",
    "country",
    "comments",
    "sensor_id",
    "description",
    "network_id",
    "col_hex",
    "vars",
    "display_names",
)


def single_item_rep(item):
    """Return representation of a single network item."""
    return {
        key: getattr(item, key)
        for key in item_keys
    }


def collection_item_rep(item):
    """Return representation of a network collection item.
    May conceivably be different than representation of a single a network.
    """
    return single_item_rep(item)


def collection_rep(items):
    """Return representation of networks collection."""
    return [collection_item_rep(item) for item in items]


def collection():
    with log_timing("List all CNG items", log=logger.debug):
        with log_timing("Query all CNG items", log=logger.debug):
            items = (
                get_app_session()
                .query(CrmpNetworkGeoserver)
                .order_by(CrmpNetworkGeoserver.network_id.asc())
                .all()
            )
        with log_timing("Convert CNG items to rep", log=logger.debug):
            return collection_rep(items)
