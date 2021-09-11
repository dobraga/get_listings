from dashboard.callbacks import sidebar, data

from dash import Dash


def init_app(dash: Dash) -> Dash:
    dash = sidebar.init_app(dash)
    dash = data.init_app(dash)

    return dash
