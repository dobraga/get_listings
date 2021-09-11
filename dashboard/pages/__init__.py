from dash import Dash

from dashboard.pages import map, table


def init_app(dash: Dash) -> Dash:
    dash = map.init_app(dash)
    dash = table.init_app(dash)
    return dash