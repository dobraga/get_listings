from dashboard.callbacks import data

from dash import Dash


def init_app(dash: Dash) -> Dash:
    dash = data.init_app(dash)

    return dash
