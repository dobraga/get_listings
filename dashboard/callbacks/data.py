import numpy as np
import pandas as pd
from dash import Dash
from math import ceil
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State


from listings.backend.location import list_locations
from listings.backend.listings import get_listings
from listings.backend.metro import get_metro

from dashboard.utils import depara_tp_contrato, depara_tp_listings


def init_app(app: Dash) -> Dash:
    @app.callback(
        Output("select_local", "options"),
        Output("select_local", "value"),
        Output("fade_search_imoveis", "is_in"),
        Input("search_local", "n_clicks"),
        State("local", "value"),
    )
    def search_local(click, value):
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
        Output("slider_preco", "min"),
        Output("slider_preco", "max"),
        Output("slider_preco", "value"),
        Output("slider_preco", "marks"),
        Output("fade_filter_imoveis", "is_in"),
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
                selected_location["stateAcronym"], app.server.config, app.db
            ),
            config=app.server.config,
            db=app.db,
        )

        ini, fim = int(df.total_fee.min()), ceil(df.total_fee.max())
        ini_log, fim_log = np.log1p(ini), np.log1p(fim)

        return (
            df.to_dict("records"),
            ini_log,
            fim_log,
            (ini_log, fim_log),
            {ini_log: {"label": str(ini)}, fim_log: {"label": str(fim)}},
            True,
        )

    @app.callback(
        Output("filtered_data", "data"),
        Output("selected_slider_preco", "children"),
        Input("data", "data"),
        Input("slider_preco", "value"),
    )
    def filter_data(data, slider_preco):
        df = pd.DataFrame(data)

        slider_preco = np.expm1(slider_preco)
        ini, fim = int(slider_preco[0]), ceil(slider_preco[1])

        df = df[(df["total_fee"] >= ini) & (df["total_fee"] <= fim)]

        return (
            df.to_dict("records"),
            "Selecionado imóveis com valores entre [{},{}]".format(ini, fim),
        )

    return app