from dashboard.extensions import conf, logger, database, serializer
from backend.settings import settings

from dash import Dash
from dynaconf import FlaskDynaconf


def init_app(dash: Dash) -> Dash:
    FlaskDynaconf(dash.server, dynaconf_instance=settings)
    dash = conf.init_app(dash)
    dash = logger.init_app(dash)
    dash = database.init_app(dash)
    dash = serializer.init_app(dash)
    return dash
