import logging
from typing import Any
from dash import Dash


log = logging.getLogger(__name__)


def init_app(dash: Dash) -> Dash:

    app = dash.server

    log_config: dict[str, Any] = {
        "level": "DEBUG" if app.config["DEBUG"] else "INFO",
        "format": "%(asctime)s %(levelname)8s (%(name)s:%(lineno)s): %(message)s",
        "datefmt": "%Y-%m-%d %H:%M:%S",
    }

    if app.config["FLASK_ENV"] == "production":
        gunicorn_logger = logging.getLogger("gunicorn.error")
        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(gunicorn_logger.level)
        log_config["level"] = gunicorn_logger.level
    else:
        log_config["filename"] = "logger.log"
        log_config["filemode"] = "w"

    logging.basicConfig(**log_config)

    return dash
