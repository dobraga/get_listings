from dash import Dash
import dash_bootstrap_components as dbc


def init_app(server):
    from dashboard import layout, callbacks

    dash = Dash(
        server=server,
        routes_pathname_prefix="/dash/",
        external_stylesheets=[
            dbc.themes.BOOTSTRAP,
            "https://use.fontawesome.com/releases/v5.12.1/css/all.css",
        ],
    )

    dash.layout = layout.layout
    dash = callbacks.init_app(dash)

    return dash.server
