from flask_sqlalchemy import SQLAlchemy
import sdpb.api


def add_routes(app):
    # app.url_map.converters['valid_year'] = ValidYearConverter
    # app.url_map.converters['int_month'] = MonthConverter

    db = SQLAlchemy(app)

    # TODO: Break this up into separate dispatchers for collections, items, etc.
    @app.route(
        '/<any(networks, variables, stations, histories):collection>',
        methods=['GET']
    )
    def dispatch_collection(**kwargs):
        return sdpb.api.dispatch_collection(db.session, **kwargs)

    @app.route(
        '/<any(networks, variables, stations, histories):collection>/<int:id>',
        methods=['GET']
    )
    def dispatch_collection_item(**kwargs):
        return sdpb.api.dispatch_collection_item(db.session, **kwargs)
