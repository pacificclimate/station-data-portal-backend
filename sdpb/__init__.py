import os
from flask import Flask
from flask_cors import CORS
from sdpb.routes import add_routes


def get_app(config_override={}):
    app = Flask(__name__)
    CORS(app)
    app.config['SQLALCHEMY_DATABASE_URI'] = \
        os.getenv('PCDS_DSN', 'postgresql://httpd@db3.pcic.uvic.ca/crmp')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config.update(config_override)
    add_routes(app)
    return app
