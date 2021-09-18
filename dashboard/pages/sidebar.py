from dash import html, dcc, Dash
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

from dashboard.styles import SIDEBAR_HIDEN, SIDEBAR_STYLE, CONTENT_STYLE, CONTENT_STYLE1
from dashboard.utils import depara_tp_contrato, depara_tp_listings
from dashboard.pages import table, map


layout = html.Div(
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
                            dbc.Label("Faixa de Preço"),
                            html.Div(
                                [
                                    dcc.Input(
                                        id="preco_min",
                                        type="number",
                                        step=500,
                                        style={"width": "48%"},
                                    ),
                                    dcc.Input(
                                        id="preco_max",
                                        type="number",
                                        step=500,
                                        style={"width": "48%", "float": "right"},
                                    ),
                                ]
                            ),
                            html.Br(),
                            dbc.Label("Quantidade de quartos"),
                            html.Div(
                                [
                                    dcc.Input(
                                        id="quarto_min",
                                        type="number",
                                        style={"width": "48%"},
                                    ),
                                    dcc.Input(
                                        id="quarto_max",
                                        type="number",
                                        style={"width": "48%", "float": "right"},
                                    ),
                                ]
                            ),
                            html.Br(),
                            html.Div(id="filter_description", style={"font-size": 13}),
                            dbc.Button(
                                "Filtra Imóveis",
                                color="primary",
                                id="filter_imoveis",
                                style={"margin-top": 20, "width": "100%"},
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


def init_app(app: Dash) -> Dash:
    @app.callback(
        Output("sidebar", "style"),
        Output("page-content", "style"),
        Output("side_click", "data"),
        Input("btn_sidebar", "n_clicks"),
        State("side_click", "data"),
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
        Input("url", "pathname"),
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
