"""
/histories API implementation

A history can have a compact or full representation. A compact representation
omits some rarely-used attributes. Both representations always contain the
`variable_uris` attribute.

The compact representation always contains the following keys:
- id
- station_name
- lon
- lat
- elevation
- province
- freq
- min_obs_time
- max_obs_time
- variable_ids

The compact representation optionally contains the following keys:
- uri (if include_uri)

The full representation includes the compact representation plus the following:
- sdate
- edate
- tz_offset
- country

Histories returned are always filtered by:
- Associated Station is published (via associated Network)
- Has at least one associated StationObservationStats
- Matches province filter (for collection)
"""
import logging
from flask import url_for
from pycds import History, VarsPerHistory, Station, StationObservationStats
from sdpb import get_app_session
from sdpb.api import variables
from sdpb.util.representation import date_rep, float_rep, obs_stats_rep
from sdpb.util.query import (
    get_all_vars_by_hx,
    add_station_network_publish_filter,
    get_all_histories_etc,
)
from sdpb.timing import log_timing


logger = logging.getLogger("sdpb")


def id_(history):
    """Sometimes we get a naked id, sometimes we get a database record"""
    if isinstance(history, int):
        return history
    # Assume it is a History-like object
    return history.id


def uri(history):
    # TODO: Using url_for approx doubles the time to convert
    #  *entire record* to rep
    return url_for("sdpb_api_histories_get", id=id_(history))


def single_item_rep(history_etc, vars=None, compact=False, include_uri=False):
    """
    Return a representation of a single history item.

    :param history_etc: A database result containing a History and its
        associated StationObservationStats.
    :param vars: Iterable containing `Variable`s or variable ids (int)
        associated with this history.
    :param compact: Boolean. Return compact or full representation.
    :return: dict
    """
    history = history_etc.History
    sos = history_etc.StationObservationStats
    rep = {
        "id": history.id,
        **({"uri": uri(history)} if include_uri else {}),
        # TODO: Why does this not contain a (possibly optional) uri for
        #   station?
        "station_name": history.station_name,
        "lon": float_rep(history.lon),
        "lat": float_rep(history.lat),
        "elevation": float_rep(history.elevation),
        "province": history.province,
        "freq": history.freq,
        **obs_stats_rep(sos),
        "variable_ids": [
            variables.id_(variable)
            for variable in vars or []
            if variable is not None
        ],
        # "variable_uris": [variables.uri(variable) for variable in vars or []],
    }
    if compact:
        return rep
    return {
        **rep,
        "sdate": date_rep(history.sdate),
        "edate": date_rep(history.edate),
        "tz_offset": history.tz_offset,
        "country": history.country,
    }


def collection_item_rep(history_etc, **kwargs):
    """
    Return representation of a history collection item.
    May conceivably be different than representation of a single a history,
    but at present they are the same.

    :param history_etc: A database result containing a History and its
        associated StationObservationStats.
    :param vars: Iterable containing `Variable`s or variable ids (int)
        associated with this history.
    :param compact: Boolean. Return compact or full representation.
    :return: dict
    """
    return single_item_rep(history_etc, **kwargs)


def collection_rep(
    histories_etc, all_vars_by_hx=None, compact=False, include_uri=False
):
    """
    Return a representation of a histories collection.

    :param histories_etc: Iterable. Each element yielded is
        a database result containing a History and its associated
        StationObservationStats.
    :param all_vars_by_hx: dict of variables associated to each history,
        keyed by history id.
    :param compact: Boolean. Return compact or full representation of each
        history.
    :return: list
    """
    """"""

    def variables_for(history):
        """Return those variables connected with a specific history."""
        with log_timing(
            f"variables_for {history.id}",
            log=None,
            # log=logger.debug,
        ):
            if all_vars_by_hx is None:
                return []
            try:
                result = all_vars_by_hx[history.id]
                return result
            except KeyError as e:
                return []

    return [
        collection_item_rep(
            history_etc,
            vars=variables_for(history_etc.History),
            compact=compact,
            include_uri=include_uri,
        )
        for history_etc in histories_etc
    ]


def get(id=None, compact=False):
    """Get a single history and associated variables from database,
    and return their representation."""
    assert id is not None
    logger.debug("get history")
    session = get_app_session()
    q = (
        session.query(History, StationObservationStats)
        .select_from(History)
        .join(Station, History.station_id == Station.id)
        .join(
            StationObservationStats,
            StationObservationStats.history_id == History.id,
        )
        .filter(History.id == id)
    )
    q = add_station_network_publish_filter(q)
    history_etc = q.one()
    logger.debug("get vars")
    variables = (
        session.query(
            VarsPerHistory.history_id.label("history_id"),
            VarsPerHistory.vars_id.label("id"),
        )
        .filter(VarsPerHistory.history_id == id)
        .order_by(VarsPerHistory.vars_id)
        .all()
    )
    logger.debug("data retrieved")
    return single_item_rep(
        history_etc, variables, compact=compact, include_uri=True
    )


def list(
    provinces=None,
    compact=False,
    group_vars_in_database=True,
    include_uri=False,
):
    """
    Get histories and associated variables from database, and return their 
    representation.
        
    :param provinces: String, in form of comma-separated list, no spaces.
        If present, return only histories whose `province` attribute match
        this value. Match means value is None or attribute occurs in list.
    :param compact: Boolean. Determines whether a compact or full/expanded
        representation is returned. A compact representation:
        - omits attributes elevation, sdate, edate, tz_offset, country
        - does not put information in attribute variables
    :param group_vars_in_database: Boolean. Perform grouping of vars by
        history id in database or in code? In db is faster.
    :return: dict
    """
    session = get_app_session()
    with log_timing("List all histories", log=logger.debug):
        histories_etc = get_all_histories_etc(session, provinces=provinces)
        all_vars_by_hx = get_all_vars_by_hx(
            session, group_in_database=group_vars_in_database
        )
        with log_timing("Convert histories etc to rep", log=logger.debug):
            return collection_rep(
                histories_etc,
                all_vars_by_hx,
                compact=compact,
                include_uri=include_uri,
            )
