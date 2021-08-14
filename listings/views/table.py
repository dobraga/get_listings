from flask import render_template, request

from listings.backend.listings import get_listings
from listings.backend.metro import get_metro


def init_app(app):
    @app.route("/table")
    def table():
        if "locationId" not in request.args.keys():
            return "Need a local", 404

        locationId = request.args["locationId"]
        neighborhood = request.args["neighborhood"]
        state = request.args["state"]
        city = request.args["city"]
        zone = request.args["zone"]
        query = request.args["query"]
        tp_contrato = request.args["tp_contrato"]
        tp_listings = request.args["tp_listings"]
        state = request.args["stateAcronym"]

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

        if query:
            df = df.query(query)

        return render_template("table.html", df=df, locationId=locationId)
