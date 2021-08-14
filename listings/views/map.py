import folium
from flask import request
from folium.plugins import MarkerCluster

from listings.backend.listings import get_listings
from listings.backend.metro import get_metro


def init_app(app):
    @app.route("/map")
    def map():
        neighborhood = request.args.get("neighborhood")
        locationId = request.args.get("locationId")
        state = request.args.get("state")
        city = request.args.get("city")
        zone = request.args.get("zone")
        query = request.args.get("query")
        tp_contrato = request.args.get("tp_contrato")
        tp_listings = request.args.get("tp_listings")
        state = request.args["stateAcronym"]

        if locationId is None:
            return "Need a local"

        df = get_listings(
            neighborhood,
            locationId,
            state,
            city,
            zone,
            tp_contrato,
            tp_listings,
            get_metro(state),
        )

        df = df.dropna(subset=["address_lat"])
        print(query)
        if query:
            df = df.query(query)

        map = folium.Map(
            location=df[["address_lat", "address_lon"]].mean().values,
            height="85%",
            tiles="http://mt.google.com/vt/lyrs=m&x={x}&y={y}&z={z}",
            attr="toner-bcg",
        )

        marker_cluster = MarkerCluster().add_to(map)

        for _, row in df.iterrows():
            html = f"<a onclick=\"window.open('{row['url']}');\" href='#'> {row['title']} </a>"

            folium.Marker(
                location=[row["address_lat"], row["address_lon"]], popup=html
            ).add_to(marker_cluster)

        return map._repr_html_()
