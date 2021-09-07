from dashboard.styles import SIDEBAR_STYLE, CONTENT_STYLE

from dash import dcc, html
import dash_bootstrap_components as dbc

navbar = dbc.Navbar(
    html.Div(
        [
            dbc.Button(
                html.I(className="fas fa-bars"),
                color="transparent",
                id="btn_sidebar",
            ),
            html.A(
                html.Span("Imóveis", className="navbar-brand mb-0 h1"),
                href="/",
                style={"color": "inherit"},
            ),
        ]
    )
)


sidebar = html.Div(
    [
        html.P("A simple sidebar layout with navigation links", className="lead"),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink("Page 1", href="/dash/page-1", id="page-1-link"),
                dbc.NavLink("Page 2", href="/dash/page-2", id="page-2-link"),
                dbc.NavLink("Page 3", href="/dash/page-3", id="page-3-link"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    id="sidebar",
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", style=CONTENT_STYLE)

layout = html.Div(
    [
        dcc.Store(id="side_click"),
        dcc.Location(id="url"),
        navbar,
        sidebar,
        content,
    ],
)
