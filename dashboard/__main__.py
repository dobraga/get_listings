from dash import Dash
import dash_bootstrap_components as dbc

from dashboard import layout, callbacks

dash = Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://use.fontawesome.com/releases/v5.12.1/css/all.css",
    ],
)

dash.layout = layout.layout
dash = callbacks.init_app(dash)


if __name__ == "__main__":
    dash.run_server(debug=True, port=8888)
