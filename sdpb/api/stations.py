"""
/stations API implementation

A station can have a compact or full representation. A compact representation
omits some rarely-used attributes in both station proper and its associated
history items (q.v.).

The compact representation always contains the following keys:
- id
- uri
- native_id
- network_uri
- histories

The full representation includes the compact representation plus the following:
- min_obs_time
- max_obs_time

Stations returned are always filtered by:
- Its associated Network is published
- Has an associated History with an associated StationObservationStats
- Matches province filter (collection)
"""
import logging
import datetime
from flask import url_for
from sqlalchemy import func
from pycds import Station, History, StationObservationStats, Obs, Variable, VarsPerHistory
from sdpb import get_app_session
from sdpb.api import networks
from sdpb.api import histories
from sdpb.api import variables
from sdpb.util.representation import date_rep, is_expanded
from sdpb.util.query import (
    get_all_histories_etc_by_station,
    get_all_vars_by_hx,
    add_station_network_publish_filter,
    add_province_filter,
)
from sdpb.timing import log_timing


logger = logging.getLogger("sdpb")


def uri(station):
    """Return uri for a station"""
    return url_for("sdpb_api_stations_single", id=station.id)


def single_item_rep(
    station_etc,
    station_histories_etc,
    all_vars_by_hx=None,
    compact=False,
    expand=None,
):
    """
    Return a representation of a single station item.

    :param station_etc: Database result containing a Station.
    :param station_histories_etc: Iterable containing histories etc.,
        associated with the station. For definition of histories etc.,
        see histories module.
    :param all_vars_by_hx: dict of variables associated to each history,
        keyed by history id.
    :param compact: Boolean. Return compact or full representation.
    :return: dict
    """
    expand_histories = is_expanded("histories", expand)

    station = getattr(station_etc, "Station", station_etc)

    if expand_histories:
        histories_rep = histories.collection_rep(
            station_histories_etc,
            all_vars_by_hx=all_vars_by_hx,
            compact=compact,
            include_uri=False,
        )
    else:
        histories_rep = [
            {"id": hx_id}
            for hx_id in station_etc.history_ids
            # {"uri": histories.uri(hx_id)} for hx_id in station_etc.history_ids
        ]
    rep = {
        "id": station.id,
        "uri": uri(station),
        "native_id": station.native_id,
        "network_uri": networks.uri(station.network),
        "histories": histories_rep,
    }
    if compact:
        return rep
    return {
        **rep,
        "min_obs_time": date_rep(station.min_obs_time),
        "max_obs_time": date_rep(station.max_obs_time),
    }


def collection_item_rep(
    station,
    station_histories_etc,
    all_vars_by_hx=None,
    compact=False,
    expand=None,
):
    """
    Return representation of a station collection item.
    May conceivably be different than representation of a single station.
    but at present they are the same.

    :param station: Database result containing a Station.
    :param station_histories_etc: Iterable containing histories etc.,
        associated with the station. For definition of histories etc.,
        see histories module.
    :param all_vars_by_hx: dict of variables associated to each history,
        keyed by history id.
    :param compact: Boolean. Return compact or full representation.
    :return: dict
    """
    return single_item_rep(
        station,
        station_histories_etc,
        all_vars_by_hx=all_vars_by_hx,
        compact=compact,
        expand=expand,
    )


def collection_rep(
    stations,
    all_histories_etc_by_station,
    all_vars_by_hx=None,
    compact=False,
    expand=None,
):
    """
    Return a representation of a stations collection.

    :param stations: Iterable. Each item is a database result from a
        Station query.
    :param all_histories_etc_by_station: dict of histories etc. assocated to
        each station, keyed by station id.
    :param all_vars_by_hx: dict of variables associated to each history,
        keyed by history id.
    :param compact: Boolean. Return compact or full representation of each
        station.
    :param expand:
    :return: dict
    """

    def histories_etc_for(station_etc):
        station = getattr(station_etc, "Station", station_etc)
        with log_timing(
            f"histories_etc_for {station.id}",
            # logging this makes the service very very slow
            # log=logger.debug,
            log=None,
        ):
            if all_histories_etc_by_station is None:
                return None
            try:
                # result = station.histories
                result = all_histories_etc_by_station[station.id]
            except KeyError:
                result = []
        return result

    return [
        collection_item_rep(
            station,
            histories_etc_for(station),
            all_vars_by_hx=all_vars_by_hx,
            compact=compact,
            expand=expand,
        )
        for station in stations
    ]


####
# /stations/{station_id}
####


def single(id=None, compact=True, expand="histories"):
    assert id is not None
    session = get_app_session()
    q = session.query(Station).select_from(Station).filter(Station.id == id)
    q = add_station_network_publish_filter(q)
    station = q.one()
    station_histories_etc = (
        session.query(History, StationObservationStats)
        .select_from(History)
        .join(
            StationObservationStats,
            StationObservationStats.history_id == History.id,
        )
        .filter_by(station_id=id)
        .order_by(History.id)
        .all()
    )
    all_vars_by_hx = get_all_vars_by_hx(session)
    return single_item_rep(
        station,
        station_histories_etc,
        all_vars_by_hx,
        compact=compact,
        expand=expand,
    )


####
# /stations/
####


def collection(
    stride=None,
    limit=None,
    offset=None,
    provinces=None,
    compact=True,
    expand="histories",
):
    """
    Get stations from database, and return their representation.

    :param stride: Integer. Include only (roughly) every stride-th station.
    :param limit: Integer. Maximum number of results.
    :param offset: Integer. Offset for result set.
    :param provinces: String, in form of comma-separated list, no spaces.
        If present, return only stations with a history whose `province`
        attribute match this value. Match means value is None or attribute
        occurs in list.
    :param compact: Boolean. Return compact rep?
    :param expand: Associated items to expand. Valid values: "histories".
    :return: list of dict
    """
    # TODO: Add include_uri param. See histories.
    logger.debug(
        f"stations.list(stride={stride}, limit={limit}, offset={offset}, "
        f"provinces={provinces}, compact={compact}, expand={expand})"
    )
    session = get_app_session()
    expand_histories = is_expanded("histories", expand)

    with log_timing("List all stations", log=logger.debug):
        with log_timing("Query all stations", log=logger.debug):
            # Note: Station is always joined with History, and stations with
            # no associated history records are not returned.
            if expand_histories:
                stations_query = session.query(Station).select_from(Station).distinct()
                all_histories_etc_by_station = get_all_histories_etc_by_station(
                    session, provinces=provinces
                )
                all_vars_by_hx = get_all_vars_by_hx(session)
            else:
                stations_query = (
                    session.query(
                        Station, func.array_agg(History.id).label("history_ids")
                    )
                    .select_from(Station)
                    .group_by(Station.id)
                )
                all_histories_etc_by_station = None
                all_vars_by_hx = None
            stations_query = stations_query.join(
                History, History.station_id == Station.id
            )
            stations_query = add_station_network_publish_filter(stations_query)
            stations_query = add_province_filter(stations_query, provinces)
            stations_query = stations_query.order_by(Station.id.asc())
            if stride:
                stations_query = stations_query.filter(Station.id % stride == 0)
            if limit:
                stations_query = stations_query.limit(limit)
            if offset:
                stations_query = stations_query.offset(offset)
            stations = stations_query.all()

        with log_timing("Convert stations to rep", log=logger.debug):
            return collection_rep(
                stations,
                all_histories_etc_by_station,
                all_vars_by_hx=all_vars_by_hx,
                compact=compact,
                expand=expand,
            )