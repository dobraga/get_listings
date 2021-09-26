import logging
from dash import Dash


def init_app(dash: Dash) -> Dash:

    app = dash.server

    log_config = {
        "level": "DEBUG" if app.config["DEBUG"] else "INFO",
        "format": "%(asctime)s %(levelname)8s (%(name)s:%(lineno)s): %(message)s",
        "datefmt": "%Y-%m-%d %H:%M:%S",
    }

    if app.config["ENV"] == "production":
        gunicorn_logger = logging.getLogger("gunicorn.error")
        app.logger.addHandler(gunicorn_logger.handlers)
    else:
        log_config["filename"] = "logger.log"
        log_config["filemode"] = "w"

    logging.basicConfig(**log_config)

    app.logger.info(f"Using config: {app.config}")

    return dash
