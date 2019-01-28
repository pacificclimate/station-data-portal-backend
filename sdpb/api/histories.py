import logging
import sys
from flask.logging import default_handler
from pycds import History, VarsPerHistory, Variable
from sdpb.api.variables import variable_uri
from sdpb.util import date_rep


logger = logging.getLogger(__name__)
logger.addHandler(default_handler)
logger.setLevel(logging.DEBUG)


def history_uri(history):
    return '/histories/{}'.format(history.id)


def history_rep(history, variables):
    """Return representation of a history"""
    logger.debug('history_rep id: {}'.format(history.id))
    return {
        'id': history.id,
        'uri': history_uri(history),
        'station_name': history.station_name,
        'lon': float(history.lon),
        'lat': float(history.lat),
        'elevation': float(history.elevation),
        'sdate': date_rep(history.sdate),
        'edate': date_rep(history.edate),
        'tz_offset': history.tz_offset,
        'province': history.province,
        'country': history.country,
        'freq': history.freq,
        'variable_uris': [variable_uri(variable) for variable in variables]
    }


def history_collection_item_rep(history, variables):
    """Return representation of a history collection item.
    May conceivably be different than representation of a single a history.
    """
    return history_rep(history, variables)


def history_collection_rep(histories, all_variables):
    """Return representation of historys collection. """

    def variables_for(history):
        """Return those variables connected with a specific history."""
        # TODO: Optimize this? E.g., currently all_variables is sorted by history_id
        return [variable for variable in all_variables
            if variable.history_id == history.id]

    return [history_collection_item_rep(history, variables_for(history))
            for history in histories]


def get_history_item_rep(session, id=None):
    """Get a single history and associated variables from database,
    and return their representation."""
    assert id is not None
    logger.debug('get history')
    history = session.query(History).filter_by(id=id).one()
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
    return history_rep(history, variables)


def get_history_collection_rep(session):
    """Get histories and associated variables from database,
    and return their representation."""
    logger.debug('get histories')
    histories = (
        session.query(History)
        .order_by(History.id.asc())
        .limit(1000)
        .all()
    )
    logger.debug('get vars')
    all_variables = (
        session.query(
            VarsPerHistory.history_id.label('history_id'),
            VarsPerHistory.vars_id.label('id'),
        )
        .order_by(
            VarsPerHistory.history_id.asc(),
            VarsPerHistory.vars_id.asc(),
        )
        .all()
    )
    logger.debug('data retrieved')
    return history_collection_rep(histories, all_variables)