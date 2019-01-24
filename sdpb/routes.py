from werkzeug.routing import IntegerConverter
from flask_sqlalchemy import SQLAlchemy
import sdpb.api

# Flask converters validate and process (including type conversion) variable parts in a route. Flask provides builtin
# converters (e.g., `any`), and users may supplement these with custom converters. We provide two custom converters:
# one to validate and covert valid <year> parts in URIs; one to validate and convert integer coded <month> parts.


class ValidYearConverter(IntegerConverter):
    """This converter only accepts integer values between 1850 and 2100::

        Rule('/page/<valid_year:value>')

    :param map: the :class:`Map`.
    :returns int: the validated value as an integer
    """
    def __init__(self, map):
        IntegerConverter.__init__(self, map, min=1850, max=2100)


class MonthConverter(IntegerConverter):
    """This converter only accepts integer values between 1 and 12 (numeric encoding for months)::

        Rule('/page/<int_month:value>')

    :param map: the :class:`Map`.
    :returns int: the validated value as an integer
    """
    def __init__(self, map):
        IntegerConverter.__init__(self, map, min=1, max=12)


def add_routes(app):
    # app.url_map.converters['valid_year'] = ValidYearConverter
    # app.url_map.converters['int_month'] = MonthConverter

    def components(collection):
        """Helper for setting up routes"""
        return {
            'collection': '<any({}):collection>'.format(collection),
        }

    db = SQLAlchemy(app)

    # @app.route('/{dataset}/{variable};{month}'.format(**components('baseline')), methods=['GET'])
    # @app.route('/{dataset}/{variable};{year}-{month}'.format(**components('weather')), methods=['GET'])
    @app.route('/<any({variables, networks, stations}):collection>', methods=['GET'])
    def dispatch(**kwargs):
        return sdpb.api.dispatch(db.session, **kwargs)
    # dispatch = partial(sdpb.api.dispatch, db.session)  # rats, this doesn't work
