from flask import request
from folium.plugins import MarkerCluster
import folium
from run import run


def init_app(app):
    @app.route("/map")
    def map():
        neighborhood = request.args.get("neighborhood")
        locationId = request.args.get("locationId")
        state = request.args.get("state")
        city = request.args.get("city")
        zone = request.args.get("zone")
        query = request.args.get("query")

        if locationId is None:
            return "Need a local"

        df, _ = run(neighborhood, locationId, state, city, zone)
        df = df.dropna(subset=["point_lat"])
        if query:
            df = df.query(query)

        map = folium.Map(
            location=df[["point_lat", "point_lon"]].mean().values,
            height="85%",
            tiles="http://mt.google.com/vt/lyrs=m&x={x}&y={y}&z={z}",
            attr="toner-bcg",
        )

        marker_cluster = MarkerCluster().add_to(map)

        for _, row in df.iterrows():
            html = f"<a onclick=\"window.open('{row['url']}');\" href='#'> {row['title']} </a>"

            folium.Marker(
                location=[row["point_lat"], row["point_lon"]], popup=html
            ).add_to(marker_cluster)

        return map._repr_html_()
