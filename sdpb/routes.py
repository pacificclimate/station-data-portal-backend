from flask_sqlalchemy import SQLAlchemy
import sdpb.api


def add_routes(app):

    db = SQLAlchemy(app)

    @app.route(
        '/<any(networks, variables, stations, histories):collection>',
        methods=['GET']
    )
    def dispatch_collection(collection):
        return sdpb.api.dispatch_collection(db.session, collection)

    @app.route(
        '/<any(networks, variables, stations, histories):collection>/<int:id>',
        methods=['GET']
    )
    def dispatch_collection_item(collection, id):
        return sdpb.api.dispatch_collection_item(db.session, collection, id)
