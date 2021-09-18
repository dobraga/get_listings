from dashboard.extensions import conf, logger, database, serializer

from dash import Dash


def init_app(dash: Dash) -> Dash:
    dash = conf.init_app(dash)
    dash = logger.init_app(dash)
    dash = database.init_app(dash)
    dash = serializer.init_app(dash)
    return dash
