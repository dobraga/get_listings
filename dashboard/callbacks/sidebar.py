from dashboard.styles import SIDEBAR_HIDEN, SIDEBAR_STYLE, CONTENT_STYLE, CONTENT_STYLE1
from dashboard.pages import table, map


from dash import html, Dash
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State


def init_app(app: Dash) -> Dash:
    @app.callback(
        [
            Output("sidebar", "style"),
            Output("page-content", "style"),
            Output("side_click", "data"),
        ],
        [Input("btn_sidebar", "n_clicks")],
        [State("side_click", "data")],
    )
    def toggle_sidebar(n, nclick):
        if n:
            if nclick == "SHOW":
                sidebar_style = SIDEBAR_HIDEN
                content_style = CONTENT_STYLE1
                cur_nclick = "HIDDEN"
            else:
                sidebar_style = SIDEBAR_STYLE
                content_style = CONTENT_STYLE
                cur_nclick = "SHOW"
        else:
            sidebar_style = SIDEBAR_STYLE
            content_style = CONTENT_STYLE
            cur_nclick = "SHOW"

        return sidebar_style, content_style, cur_nclick

    @app.callback(
        Output("page-content", "children"),
        [Input("url", "pathname")],
    )
    def render_page_content(pathname):
        if pathname in ["", "/", "/dash", "/dash/table"]:
            return table.layout
        elif pathname == "/dash/map":
            return map.layout

        # If the user tries to reach a different page, return a 404 message
        return dbc.Jumbotron(
            [
                html.H1("404: Not found", className="text-danger"),
                html.Hr(),
                html.P(f"The pathname {pathname} was not recognised..."),
            ]
        )

    return app
