from dash import Dash
import dash_bootstrap_components as dbc

from dashboard import layout, extensions, pages, callbacks


def create_app() -> Dash:
    dash = Dash(
        __name__,
        external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
        suppress_callback_exceptions=True,
    )

    dash.layout = layout.layout
    dash = extensions.init_app(dash)
    dash = callbacks.init_app(dash)
    dash = pages.init_app(dash)

    return dash


def create_server():
    return create_app().server
