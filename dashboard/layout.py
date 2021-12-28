from dash import dcc, html
import dash_bootstrap_components as dbc

from dashboard.pages import sidebar
from dashboard.styles import CONTENT_STYLE

# TODO: Melhoria no css das páginas
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

layout = dcc.Loading(
    id="loading",
    children=html.Div(
        [
            dcc.Store(id="data"),
            dcc.Store(id="filtered_data"),
            dcc.Store(id="side_click"),
            dcc.Location(id="url"),
            navbar,
            sidebar.layout,
            html.Div(id="page-content", style=CONTENT_STYLE),
        ],
    ),
)
