from dynaconf import FlaskDynaconf
from dash import Dash


def init_app(dash: Dash) -> Dash:
    FlaskDynaconf(dash.server)
    return dash
