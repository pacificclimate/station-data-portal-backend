import time
import logging
from flask import url_for
from flask.logging import default_handler
from pycds import History, VarsPerHistory, Network, Station
from sdpb import get_app_session
from sdpb.api import variables
from sdpb.util import date_rep, float_rep, get_all_vars_by_hx, set_logger_level_from_qp


logger = logging.getLogger(__name__)
logger.addHandler(default_handler)
logger.setLevel(logging.INFO)


def uri(history):
    return url_for('.sdpb_api_histories_get', id=history.id)


def single_item_rep(history, vars):
    """Return representation of a history"""
    set_logger_level_from_qp(logger)
    logger.debug('history_rep id: {}'.format(history.id))
    return {
        'id': history.id,
        'uri': uri(history),
        'station_name': history.station_name,
        'lon': float_rep(history.lon),
        'lat': float_rep(history.lat),
        'elevation': float_rep(history.elevation),
        'sdate': date_rep(history.sdate),
        'edate': date_rep(history.edate),
        'tz_offset': history.tz_offset,
        'province': history.province,
        'country': history.country,
        'freq': history.freq,
        'variable_uris': [variables.uri(variable) for variable in vars]
    }


def collection_item_rep(history, variables):
    """Return representation of a history collection item.
    May conceivably be different than representation of a single a history.
    """
    set_logger_level_from_qp(logger)
    return single_item_rep(history, variables)


def collection_rep(histories, all_vars_by_hx):
    """Return representation of historys collection. """

    def variables_for(history):
        """Return those variables connected with a specific history."""
        logger.debug('variables_for({})'.format(history.id))
        start_time = time.time()
        try:
            result = all_vars_by_hx[history.id]
            logger.debug(
                'variables_for({}) elapsed time: {}'
                    .format(history.id, time.time() - start_time)
            )
            return result
        except Exception as e:
            logger.debug(
                'Exception retrieving all_vars_by_hx[{}]: {}'
                    .format(history.id, e)
            )
            return []

    set_logger_level_from_qp(logger)
    return [collection_item_rep(history, variables_for(history))
            for history in histories]


def get(id=None):
    """Get a single history and associated variables from database,
    and return their representation."""
    set_logger_level_from_qp(logger)
    assert id is not None
    logger.debug('get history')
    session = get_app_session()
    history = (
        session.
            query(History)
            .select_from(History)
            .join(Station, History.station_id_id == Station.id)
            .join(Network, Station.network_id == Network.id)
            .filter(History.id==id, Network.publish==True)
            .one()
    )
    logger.debug('get vars')
    variables = (
        session.query(
            VarsPerHistory.history_id.label('history_id'),
            VarsPerHistory.vars_id.label('id'),
        )
        .filter(VarsPerHistory.history_id == history.id)
        .order_by(VarsPerHistory.vars_id)
        .all()
    )
    logger.debug('data retrieved')
    return single_item_rep(history, variables)


def list():
    """Get histories and associated variables from database,
    and return their representation."""
    set_logger_level_from_qp(logger)
    logger.debug('get histories')
    session = get_app_session()
    histories = (
        session
            .query(History)
            .select_from(History)
            .join(Station, History.station_id == Station.id)
            .join(Network, Station.network_id == Network.id)
            .filter(Network.publish==True)
            .order_by(History.id.asc())
        .all()
    )
    logger.debug('histories retrieved')
    all_vars_by_hx = get_all_vars_by_hx(session)
    return collection_rep(histories, all_vars_by_hx)