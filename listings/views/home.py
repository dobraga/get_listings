from listings.backend.location import list_locations

from flask import render_template, url_for, redirect, request


def init_app(app):
    @app.route("/", methods=["GET", "POST"])
    def home():
        local = ""
        locations = []
        depara_tp_contrato = {"Aluguel": "RENTAL", "Compra": "SALE"}
        depara_tp_listings = {"Usado": "USED", "Novo": "DEVELOPMENT"}

        if request.method == "POST":
            local = request.form["local"]
            locations = list_locations(request.form["local"])

            if "selected_local" in request.form.keys():
                selected_local, tp_contrato, tp_listings, query = (
                    request.form["selected_local"],
                    request.form["tp_contrato"],
                    request.form["tp_listings"],
                    request.form.get("query", ""),
                )
                tp_contrato = depara_tp_contrato[tp_contrato]
                tp_listings = depara_tp_listings[tp_listings]
                selected_local = locations[selected_local]

                if "submit-table" in request.form.keys():
                    endpoint = "table"
                elif "submit-dash" in request.form.keys():
                    endpoint = "/dash/"
                else:
                    endpoint = "map"

                url = url_for(
                    endpoint,
                    local=local,
                    query=query,
                    tp_contrato=tp_contrato,
                    tp_listings=tp_listings,
                    **selected_local
                )

                return redirect(url)

        return render_template(
            "home.html",
            local=local,
            locations=locations,
            depara_tp_contrato=depara_tp_contrato,
            depara_tp_listings=depara_tp_listings,
        )
