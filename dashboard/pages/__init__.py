from dash import Dash

from dashboard.pages import map, table, sidebar


def init_app(dash: Dash) -> Dash:
    dash = sidebar.init_app(dash)
    dash = map.init_app(dash)
    dash = table.init_app(dash)
    return dash
