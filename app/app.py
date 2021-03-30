from flask import Flask, render_template, request, jsonify
from folium.plugins import MarkerCluster
from app.extensions import appearance
from run import run
import folium
import json

app = Flask(__name__)

appearance.init_app(app)


@app.route("/")
def index():
    local = request.args.get("local")
    query = request.args.get("query")

    if local is None:
        return "Need a local"

    df, local = run(local)
    app.logger.info(f"Columns: {df.columns.values.tolist()}")

    if query:
        df = df.query(query)

    return jsonify(json.loads(df.to_json(orient="records")))  # ))


@app.route("/table")
def table():
    local = request.args.get("local")
    query = request.args.get("query")

    if local is None:
        return "Need a local"

    df, local = run(local)
    app.logger.info(f"Columns: {df.columns.values.tolist()}")

    if query:
        df = df.query(query)
    return render_template("index.html", df=df, local=local)


@app.route("/map")
def map():
    local = request.args.get("local")
    query = request.args.get("query")

    if local is None:
        return "Need a local"

    df, local = run(local)
    df = df.query(query).dropna(subset=["point_lat"])

    map = folium.Map(
        location=df[["point_lat", "point_lon"]].mean().values,
        height="85%",
        tiles="http://mt.google.com/vt/lyrs=m&x={x}&y={y}&z={z}",
        attr="toner-bcg",
    )

    marker_cluster = MarkerCluster().add_to(map)

    for _, row in df.iterrows():
        html = (
            f"<a onclick=\"window.open('{row['url']}');\" href='#'> {row['title']} </a>"
        )

        folium.Marker(location=[row["point_lat"], row["point_lon"]], popup=html).add_to(
            marker_cluster
        )

    return map._repr_html_()
