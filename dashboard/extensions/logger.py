import logging
from dash import Dash


def init_app(dash: Dash) -> Dash:

    app = dash.server

    if app.config["ENV"] == "production":
        gunicorn_logger = logging.getLogger("gunicorn.error")
        app.logger.addHandler(gunicorn_logger.handlers)

    level = logging.DEBUG if app.config["DEBUG"] else logging.INFO

    logging.basicConfig(
        format="%(asctime)s %(levelname)8s (%(name)s:%(lineno)s): %(message)s",
        level=level,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    app.logger.debug(f"Using config: {app.config}")

    return dash
