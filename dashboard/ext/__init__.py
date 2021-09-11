from dashboard.ext import conf, logger, database

from dash import Dash


def init_app(dash: Dash) -> Dash:
    dash = conf.init_app(dash)
    dash = logger.init_app(dash)
    dash = database.init_app(dash)
    return dash
