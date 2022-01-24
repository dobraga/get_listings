from dash import Dash
from dash._utils import AttributeDict

from backend.settings import settings


def init_app(dash: Dash) -> Dash:
    dash.config = AttributeDict({**dash.config, **settings})
    dash.server.config.update(settings)
    return dash
