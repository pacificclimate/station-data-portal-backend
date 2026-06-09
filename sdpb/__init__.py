import logging
import os
from typing import Any
import connexion
from flask import jsonify, request
from flask_compress import Compress
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from sqlalchemy.pool import NullPool
from starlette.middleware.cors import CORSMiddleware

logger = logging.getLogger(__name__)

# This is a nasty way to do this.
#
# But at least the clients of this module (are supposed to) use
# `get_app_session()` instead of importing these globals directly.
# It would be better to hide these globals inside a singleton class, but that
# would take more time than I am willing to spend for an essentially isomorphic
# solution.
#
# Note: Clients (API functions) *must* use `get_app_session()`. If instead they
# import these globals directly, the tests fail because their values are
# captured by the test framework before they are set to a non-None value.

connexion_app = None
flask_app = None
app_db = None


compress = Compress()


def _build_engine_options() -> dict[str, Any]:
    """Build SQLAlchemy engine options from environment variables.

    Set SQLALCHEMY_POOL_CLASS=null to use NullPool (recommended when deploying
    behind pgbouncer). Optional pool tuning via SQLALCHEMY_POOL_SIZE,
    SQLALCHEMY_MAX_OVERFLOW, SQLALCHEMY_POOL_TIMEOUT, SQLALCHEMY_POOL_RECYCLE.
    """
    if os.getenv("SQLALCHEMY_POOL_CLASS", "").lower() == "null":
        return {"poolclass": NullPool}

    options: dict[str, Any] = {"pool_pre_ping": True}

    for env_var, key, cast in [
        ("SQLALCHEMY_POOL_SIZE", "pool_size", int),
        ("SQLALCHEMY_MAX_OVERFLOW", "max_overflow", int),
        ("SQLALCHEMY_POOL_TIMEOUT", "pool_timeout", float),
        ("SQLALCHEMY_POOL_RECYCLE", "pool_recycle", float),
    ]:
        val = os.getenv(env_var)
        if val is not None:
            options[key] = cast(val)

    return options


def create_app(config_override={}):
    global connexion_app, flask_app, app_db
    connexion_app = connexion.FlaskApp(__name__, specification_dir="openapi/")

    flask_app = connexion_app.app
    flask_app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI=os.getenv(
            "PCDS_DSN", "postgresql://httpd@db.pcic.uvic.ca/crmp"
        ),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ECHO=False,
        COMPRESS_ALGORITHM="gzip",
        SQLALCHEMY_ENGINE_OPTIONS=_build_engine_options(),
    )
    flask_app.config.update(config_override)
    compress.init_app(flask_app)

    app_db = SQLAlchemy(flask_app)

    @flask_app.route("/readyz")
    def readyz():
        status = {"status": "ok"}
        http_status = 200
        if request.args.get("verbose", "").lower() in ("1", "true", "yes"):
            try:
                get_app_session().execute(text("SELECT 1"))
                status["db"] = "ok"
            except Exception as e:
                status["status"] = "error"
                status["db"] = str(e)
                http_status = 503
        response = jsonify(status)
        response.cache_control.no_store = True
        return response, http_status

    @flask_app.errorhandler(Exception)
    def log_unhandled_exception(e):
        logger.exception("Unhandled exception")
        raise e

    # Must establish database before adding API spec(s). API specs refer to
    # handlers (`operationId`), which in turn import the database.
    # If you try to add the API spec before the database is defined, then the
    # import fails. This is a consequence of this particular project structure,
    # but it is (otherwise) a nice one and worth imposing this little bit of
    # ordering during setup.

    connexion_app.add_api("api-spec.yaml")
    connexion_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return connexion_app, flask_app, app_db


def get_app_db():
    return app_db


def get_app_session():
    return app_db.session
