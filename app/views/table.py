from flask import render_template, request
from run import run


def init_app(app):
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

        df, _ = run(neighborhood, locationId, state, city, zone)
        app.logger.info(f"Columns: {df.columns.values.tolist()}")

        if query:
            df = df.query(query)
        return render_template("table.html", df=df, locationId=locationId)
