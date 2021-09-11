from dash import dcc, html
from dash.html.Div import Div
import dash_bootstrap_components as dbc

from dashboard.styles import SIDEBAR_STYLE, CONTENT_STYLE
from dashboard.utils import depara_tp_contrato, depara_tp_listings

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
        dbc.Nav(
            [
                dbc.NavLink("Tabela", href="/", active="exact"),
                dbc.NavLink("Mapa", href="/dash/map", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
        html.Hr(),
        html.Div(
            [
                dbc.Label("Tipo do Imóvel"),
                dbc.InputGroup(
                    [
                        dbc.Select(
                            id="business_type",
                            options=depara_tp_contrato,
                            value="RENTAL",
                            style={"margin-right": 5},
                        ),
                        dbc.Select(
                            id="listing_type", value="USED", options=depara_tp_listings
                        ),
                    ],
                    style={"margin-bottom": 20},
                ),
                dbc.Label("Busca Local"),
                dbc.InputGroup(
                    [
                        dbc.Input(
                            id="local",
                            placeholder="Local",
                            style={"margin-right": 5},
                        ),
                        dbc.Button("Procurar", color="primary", id="search_local"),
                    ]
                ),
                dbc.Fade(
                    html.Div(
                        [
                            dbc.Select(
                                id="select_local",
                                style={"margin-top": 5, "margin-bottom": 5},
                            ),
                            dbc.Button(
                                "Procurar Imóveis",
                                color="primary",
                                id="search_imoveis",
                                style={"margin-bottom": 20, "width": "100%"},
                            ),
                        ]
                    ),
                    id="fade_search_imoveis",
                    is_in=False,
                ),
            ]
        ),
        dbc.Fade(
            html.Div(
                [
                    html.Hr(),
                    html.Div(
                        [
                            dbc.Label("Filtra preço"),
                            dcc.RangeSlider(
                                id="slider_preco",
                                allowCross=False,
                                step=0.01,
                                updatemode="drag",
                            ),
                            html.Div(
                                id="selected_slider_preco", style={"font-size": 13}
                            ),
                        ]
                    ),
                ]
            ),
            id="fade_filter_imoveis",
            is_in=False,
        ),
    ],
    id="sidebar",
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", style=CONTENT_STYLE)

layout = html.Div(
    [
        dcc.Store(id="data"),
        dcc.Store(id="filtered_data"),
        dcc.Store(id="side_click"),
        dcc.Location(id="url"),
        navbar,
        sidebar,
        content,
    ],
)
