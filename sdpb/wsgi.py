import logging.config
import os
import yaml

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

from sdpb import create_app

if os.path.exists("logging.yaml"):
    logging.config.dictConfig(yaml.safe_load(open("logging.yaml")))
logger = logging.getLogger("sdpb")
logger.info("Creating app")

connexion_app, flask_app, app_db = create_app()
