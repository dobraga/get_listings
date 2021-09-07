from dashboard.styles import SIDEBAR_HIDEN, SIDEBAR_STYLE, CONTENT_STYLE, CONTENT_STYLE1

from dash import html, Dash
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State


def init_app(app: Dash):
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

    # this callback uses the current pathname to set the active state of the
    # corresponding nav link to true, allowing users to tell see page they are on
    @app.callback(
        [Output(f"page-{i}-link", "active") for i in range(1, 4)],
        [Input("url", "pathname")],
    )
    def toggle_active_links(pathname):
        if pathname == "/":
            # Treat page 1 as the homepage / index
            return True, False, False
        return [pathname == f"/dash/page-{i}" for i in range(1, 4)]

    @app.callback(
        Output("page-content", "children"),
        [Input("url", "pathname")],
    )
    def render_page_content(pathname):
        if pathname in ["/", "/dash/", "/dash/page-1"]:
            return html.P("This is the content of page 1!")
        elif pathname == "/dash/page-2":
            return html.P("This is the content of page 2. Yay!")
        elif pathname == "/dash/page-3":
            return html.P("Oh cool, this is page 3!")
        # If the user tries to reach a different page, return a 404 message
        return dbc.Jumbotron(
            [
                html.H1("404: Not found", className="text-danger"),
                html.Hr(),
                html.P(f"The pathname {pathname} was not recognised..."),
            ]
        )

    return app
