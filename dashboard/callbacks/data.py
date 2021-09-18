import numpy as np
import pandas as pd
from dash import Dash
from math import ceil
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State


from backend.metro import get_metro
from backend.location import list_locations
from backend.get_listings import get_listings

from dashboard.utils import depara_tp_contrato, depara_tp_listings


def min_max(values: pd.Series, plus=0):
    ini, fim = values.min(), values.max()
    ini, fim = int(int(ini / plus)) * plus, int(ceil(fim / plus)) * plus
    return ini, ini, fim, fim, ini, fim


def init_app(app: Dash) -> Dash:
    @app.callback(
        Output("select_local", "options"),
        Output("select_local", "value"),
        Output("fade_search_imoveis", "is_in"),
        Input("search_local", "n_clicks"),
        State("local", "value"),
    )
    def search_local(_, value):
        if not value:
            raise PreventUpdate

        locations = list_locations(value)

        if locations:
            return (
                [{"label": k, "value": v} for k, v in locations.items()],
                list(locations.keys())[0],
                True,
            )

    @app.callback(
        Output("data", "data"),
        Output("fade_filter_imoveis", "is_in"),
        Output("preco_min", "value"),
        Output("preco_min", "min"),
        Output("preco_min", "max"),
        Output("preco_max", "value"),
        Output("preco_max", "min"),
        Output("preco_max", "max"),
        Output("quarto_min", "value"),
        Output("quarto_min", "min"),
        Output("quarto_min", "max"),
        Output("quarto_max", "value"),
        Output("quarto_max", "min"),
        Output("quarto_max", "max"),
        Input("search_imoveis", "n_clicks"),
        State("select_local", "options"),
        State("select_local", "value"),
        State("business_type", "value"),
        State("listing_type", "value"),
    )
    def search_imoveis(_, options, value, business_value, listing_value):
        if not value:
            raise PreventUpdate

        selected_location = [o for o in options if o["label"] == value][0]["value"]

        business_type = [o for o in depara_tp_contrato if o["value"] == business_value]
        business_type = business_type[0]["value"]

        listing_type = [o for o in depara_tp_listings if o["value"] == listing_value]
        listing_type = listing_type[0]["value"]

        df = get_listings(
            **selected_location,
            business_type=business_type,
            listing_type=listing_type,
            df_metro=get_metro(
                selected_location["stateAcronym"], app.server.config, app.server.db
            ),
            config=app.server.config,
            db=app.server.db,
        )

        return (
            df.to_dict("records"),
            True,
            *min_max(df.total_fee, 500),
            *min_max(df.bedrooms, 1),
        )

    @app.callback(
        Output("filter_description", "children"),
        Input("preco_min", "value"),
        Input("preco_max", "value"),
        Input("quarto_min", "value"),
        Input("quarto_max", "value"),
    )
    def describe_filter(*args):
        if [arg for arg in args if arg is None]:
            raise PreventUpdate

        return "Selecionado imóveis com valores entre [{},{}] e que possuam a quantidade [{},{}] de quartos".format(
            *args
        )

    @app.callback(
        Output("filtered_data", "data"),
        Input("filter_imoveis", "n_clicks"),
        Input("data", "data"),
        State("preco_min", "value"),
        State("preco_max", "value"),
        State("quarto_min", "value"),
        State("quarto_max", "value"),
    )
    def filter_data(n_clicks, data, preco_min, preco_max, quarto_min, quarto_max):
        if n_clicks is None and data is None:
            raise PreventUpdate

        df = pd.DataFrame(data)

        df = df[
            (df["total_fee"] >= preco_min)
            & (df["total_fee"] <= preco_max)
            & (df["bedrooms"] >= quarto_min)
            & (df["bedrooms"] <= quarto_max)
        ]

        return df.to_dict("records")

    return app
