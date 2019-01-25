from flask_sqlalchemy import SQLAlchemy
import sdpb.api


def add_routes(app):
    # app.url_map.converters['valid_year'] = ValidYearConverter
    # app.url_map.converters['int_month'] = MonthConverter

    def components(collection):
        """Helper for setting up routes"""
        return {
            'collection': '<any({}):collection>'.format(collection),
        }

    db = SQLAlchemy(app)

    @app.route(
        '/<any(networks, variables, stations):collection>',
        methods=['GET']
    )
    @app.route(
        '/<any(networks, variables, stations):collection>/<int:id>',
        methods=['GET']
    )
    def dispatch(**kwargs):
        return sdpb.api.dispatch(db.session, **kwargs)
    # dispatch = partial(sdpb.api.dispatch, db.session)  # rats, this doesn't work
