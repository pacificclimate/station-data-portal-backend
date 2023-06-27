import logging.config
import yaml
from sdpb import create_app

logging.config.dictConfig(yaml.safe_load(open("logging.yaml")))
logger = logging.getLogger("sdpb")
logger.info("Creating app")

connexion_app, flask_app, app_db = create_app()
