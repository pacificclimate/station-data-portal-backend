import os
import connexion
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

# This is a horrible way to do this.
connexion_app = None
flask_app = None
app_db = None


def create_app(config_override = {}):
    global connexion_app, flask_app, app_db
    connexion_app = connexion.FlaskApp(__name__, specification_dir='openapi/')

    flask_app = connexion_app.app
    CORS(flask_app)
    flask_app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI=
        os.getenv('PCDS_DSN', 'postgresql://httpd@db3.pcic.uvic.ca/crmp'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ECHO=False,
    )
    flask_app.config.update(config_override)

    app_db = SQLAlchemy(flask_app)

    # Must establish database before adding API spec(s). API specs refer to
    # handlers (`operationId`), which in turn import the database.
    # If you try to add the API spec before the database is defined, then the
    # import fails. This is a consequence of this particular project structure,
    # but it is (otherwise) a nice one and worth imposing this little bit of
    # ordering during setup.

    connexion_app.add_api('api-spec.yaml')

    print('##### app initialized')

    return connexion_app, flask_app, app_db