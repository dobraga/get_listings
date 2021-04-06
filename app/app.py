from flask import Flask, render_template, request, jsonify, url_for, redirect
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired
from folium.plugins import MarkerCluster
from flask_wtf import FlaskForm
from run import run
from get_listings.location import list_locations
from get_listings._config import Configurations
import folium
import json

conf = Configurations()

app = Flask(__name__)


class homepage(FlaskForm):
    local = StringField("local", validators=[DataRequired()])
    query = StringField("query")
    search = SubmitField("Search")
    submit_table = SubmitField("Table")
    submit_map = SubmitField("Map")

    checkbox0 = BooleanField("checkbox0")
    checkbox1 = BooleanField("checkbox1")
    checkbox2 = BooleanField("checkbox2")
    checkbox3 = BooleanField("checkbox3")
    checkbox4 = BooleanField("checkbox4")
    checkbox5 = BooleanField("checkbox5")


@app.route("/", methods=["GET", "POST"])
def home():
    form = homepage(meta={"csrf": False})

    if form.validate_on_submit():
        if form.search.data:
            locations = list_locations(conf, form.local.data)
            return render_template("home.html", form=form, locations=locations)

        else:
            locations = list_locations(conf, form.local.data)
            local = {}

            for i, checkbox in enumerate(
                [
                    form.checkbox0.data,
                    form.checkbox1.data,
                    form.checkbox2.data,
                    form.checkbox3.data,
                    form.checkbox4.data,
                    form.checkbox5.data,
                ]
            ):
                if checkbox:
                    local = locations[i]

            if not local:
                return render_template("home.html", form=form, locations=[])

            elif form.submit_table.data:
                url = url_for("table", query=form.query.data, **local)

            elif form.submit_map.data:
                url = url_for("map", query=form.query.data, **local)

            return redirect(url)

    return render_template("home.html", form=form, locations=[])


@app.route("/api")
def api():
    neighborhood = request.args.get("neighborhood")
    locationId = request.args.get("locationId")
    state = request.args.get("state")
    city = request.args.get("city")
    zone = request.args.get("zone")
    query = request.args.get("query")

    if locationId is None:
        return "Need a local"

    df, _ = run(neighborhood, locationId, state, city, zone)
    app.logger.info(f"Columns: {df.columns.values.tolist()}")

    if query:
        df = df.query(query)

    return jsonify(json.loads(df.to_json(orient="records")))


@app.route("/table")
def table():
    neighborhood = request.args.get("neighborhood")
    locationId = request.args.get("locationId")
    state = request.args.get("state")
    city = request.args.get("city")
    zone = request.args.get("zone")
    query = request.args.get("query")

    if locationId is None:
        return "Need a local"

    df, local = run(neighborhood, locationId, state, city, zone)
    app.logger.info(f"Columns: {df.columns.values.tolist()}")

    if query:
        df = df.query(query)
    return render_template("table.html", df=df, locationId=locationId)


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

    df, local = run(neighborhood, locationId, state, city, zone)
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
        html = (
            f"<a onclick=\"window.open('{row['url']}');\" href='#'> {row['title']} </a>"
        )

        folium.Marker(location=[row["point_lat"], row["point_lon"]], popup=html).add_to(
            marker_cluster
        )

    return map._repr_html_()


if __name__ == "__main__":
    app.run()
