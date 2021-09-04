from geopy.distance import distance
import pandas as pd


def get_min_dist(df_metro, lat, lng):
    """
    Pega estaçao mais proxima da latlong passada
    """
    X = df_metro.copy()
    X["distance"] = X[["lat", "lng"]].apply(
        lambda x: distance((x[0], x[1]), (lat, lng)).m, axis=1
    )
    return (
        X.sort_values("distance")
        .reset_index()
        .loc[0, ["linha", "estacao", "distance"]]
        .tolist()
    )


def to_numeric(value):
    if isinstance(value, list):
        if len(value) == 0:
            return None
        value = value[0]

    if isinstance(value, (int, float)):
        return value

    if value:
        if "." in value:
            return float(value)
        return int(value)
    else:
        return None


def preprocess(
    data: dict, business_type: str = None, df_metro: pd.DataFrame = pd.DataFrame()
) -> tuple:
    parsed_columns = {}

    listing = data["listing"]

    parsed_columns["title"] = listing["title"] or listing["description"][:40]
    parsed_columns["amenities"] = listing["amenities"]
    parsed_columns["usable_area"] = to_numeric(listing["usableAreas"])
    parsed_columns["floors"] = to_numeric(listing["floors"]) or 0
    parsed_columns["units_on_the_floor"] = to_numeric(listing["unitsOnTheFloor"])
    parsed_columns["unit_floor"] = to_numeric(listing["unitFloor"])
    parsed_columns["type_unit"] = listing["unitTypes"][0]
    parsed_columns["bedrooms"] = to_numeric(listing["bedrooms"])
    parsed_columns["bathrooms"] = to_numeric(listing["bathrooms"])
    parsed_columns["suites"] = to_numeric(listing["suites"]) or 0
    parsed_columns["parking_spaces"] = to_numeric(listing["parkingSpaces"]) or 0

    pricingInfos = [
        p for p in listing["pricingInfos"] if p["businessType"] == business_type
    ][0]

    parsed_columns["price"] = to_numeric(pricingInfos.get("price"))
    parsed_columns["condo_fee"] = to_numeric(pricingInfos.get("monthlyCondoFee"))

    parsed_columns["total_fee"] = parsed_columns["price"]
    if parsed_columns["condo_fee"] is not None:
        parsed_columns["total_fee"] = (
            parsed_columns["price"] + parsed_columns["condo_fee"]
        )

    address = listing["address"]

    if "point" not in address.keys():
        address["point"] = {}

    parsed_columns["address_lat"] = address["point"].get("lat")
    parsed_columns["address_lon"] = address["point"].get("lon")

    street, streetNumber, neighborhood, complement = (
        address.get("street"),
        address.get("streetNumber"),
        address.get("neighborhood"),
        address.get("complement"),
    )

    if streetNumber:
        parsed_columns["address"] = f"{street}, {streetNumber} - {neighborhood}"
    elif street:
        parsed_columns["address"] = f"{street} - {neighborhood}"
    else:
        parsed_columns["address"] = f"{neighborhood}"

    if complement:
        parsed_columns["address"] += f" ({complement})"

    linha, estacao, distance = "", "", 0
    if df_metro.shape[0] > 0:
        if parsed_columns["address_lat"]:
            linha, estacao, distance = get_min_dist(
                df_metro, parsed_columns["address_lat"], parsed_columns["address_lon"]
            )

    parsed_columns["linha"] = linha
    parsed_columns["estacao"] = estacao
    parsed_columns["distance"] = distance

    if data["medias"]:
        parsed_columns["images"] = [
            i["url"].format(action="crop", width="264", height="200")
            for i in data["medias"]
        ]

    parsed_columns["createdAt"] = pd.to_datetime(listing["createdAt"])
    parsed_columns["updatedAt"] = pd.to_datetime(listing["updatedAt"])

    return data, parsed_columns
