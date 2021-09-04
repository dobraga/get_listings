import folium
import locale
from flask import request
from folium.plugins import MarkerCluster


from listings.backend.listings import get_listings
from listings.backend.metro import get_metro

locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")


def to_currency(value):
    return locale.currency(value, grouping=True, symbol=None)


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
            app.config["force_update"],
        )

        df = df.dropna(subset=["address_lat"])
        if query:
            df = df.query(query)

        map = folium.Map(
            location=df[["address_lat", "address_lon"]].mean().values,
            height="85%",
            tiles="https://{s}.tile.openstreetmap.de/tiles/osmde/{z}/{x}/{y}.png",
            attr="toner-bcg",
        )

        marker_cluster = MarkerCluster().add_to(map)

        base_style = "white-space: nowrap; overflow: hidden; text-overflow: ellipsis;"

        def format_template(**kwargs) -> str:
            if kwargs["business_type"] == "RENTAL":
                preco = """
                <p>
                    <span> Valor {price}/Mês |</span>
                    <span> Valor Condomínio {condo_fee}/Mês |</span>
                    <span> total {total_fee}/Mês </span>
                </p>
                """.format(
                    price=to_currency(kwargs["price"]),
                    condo_fee=to_currency(kwargs["condo_fee"]),
                    total_fee=to_currency(kwargs["total_fee"]),
                )
            else:
                preco = """
                <p>
                    <span> Valor {price} |</span>
                    <span> Valor Condomínio {condo_fee}/Mês |</span>
                    <span> total {price} </span>
                </p>
                """.format(
                    price=to_currency(kwargs["price"]),
                    condo_fee=to_currency(kwargs["condo_fee"]),
                )

            return """
            <div onclick="window.open('{url}');" style="cursor: pointer; width: 40vw; height: 20vh;">
                <div style="float: left; width: 40%">
                    <img src="{image}" style="width: 100%; height: 100%; ">
                </div>

                <div style="float: right; width: 58%; height: 100%">
                    <div style="width: 100%;">
                        <div title="{address}" style = "{style}"> {address} </div>
                        <p title="{title}" style = "{style}"> {title} </p>
                        {preco}
                        <p style = "{style}" title="{amenities}"> {amenities} </p>
                    </div>
                </div>
            </div>
            """.format(
                url=kwargs["url"],
                address=kwargs["address"],
                title=kwargs["title"],
                amenities=kwargs["amenities"],
                style=base_style,
                image=kwargs["images"][0],
                preco=preco,
            )

        for _, row in df.iterrows():
            folium.Marker(
                location=[row["address_lat"], row["address_lon"]],
                popup=format_template(**row),
            ).add_to(marker_cluster)

        return map._repr_html_()
