from dash import Dash
import dash_bootstrap_components as dbc

from dashboard import layout, ext, pages, callbacks

dash = Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://use.fontawesome.com/releases/v5.12.1/css/all.css",
    ],
    suppress_callback_exceptions=True,
)

dash.layout = layout.layout
dash = ext.init_app(dash)
dash = callbacks.init_app(dash)
dash = pages.init_app(dash)


if __name__ == "__main__":
    dash.run_server(debug=True)
