import pandas as pd
from dash import html, Dash
from folium import Map, Marker
from folium.plugins import MarkerCluster
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output

from dashboard.components.box import box

layout = html.Div(
    [
        html.Div(id="qtd_sem_latlon"),
        html.Iframe(
            id="map",
            srcDoc=Map(height="89%")._repr_html_(),
            width="100%",
            height="800px",
        ),
    ]
)


def init_app(app: Dash) -> Dash:
    @app.callback(
        Output(component_id="qtd_sem_latlon", component_property="children"),
        Output("map", "srcDoc"),
        Input("filtered_data", "data"),
    )
    def create_map(data):
        if not data:
            raise PreventUpdate

        df = pd.DataFrame(data)
        qtd_sem_latlon = df[["address_lat", "address_lon"]].isna().max(axis=1).sum()
        df = df.dropna(subset=["address_lat", "address_lon"])

        map = Map(
            location=df[["address_lat", "address_lon"]].mean().values,
            height="89%",
            tiles="https://{s}.tile.openstreetmap.de/tiles/osmde/{z}/{x}/{y}.png",
            attr="toner-bcg",
        )

        marker_cluster = MarkerCluster().add_to(map)

        for _, row in df.iterrows():
            Marker(
                location=[row["address_lat"], row["address_lon"]],
                popup=box(**row),
            ).add_to(marker_cluster)

        return f"{qtd_sem_latlon} imóveis sem latitude ou longitude", map._repr_html_()

    return app
