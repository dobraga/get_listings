from geopy.distance import distance
from os.path import join
import pandas as pd
import logging

log = logging.getLogger(__name__)


def get_min_dist(df_metro, lat, lng):
    """
    Pega estaçao mais proxima da latlong passada
    """

    if not pd.isna(lat):
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
    else:
        return ["", "", None]


def preprocess(conf, data, file_metro="metro.jsonlines"):
    log.info("Preprocessamento iniciado")

    df_metro = pd.read_json(join(conf["dir_input"], file_metro), lines=True)
    df_metro = df_metro.drop_duplicates()

    df = pd.json_normalize(data, sep="_")
    df = df.groupby(["url"]).head(1)

    df.loc[:, "media"] = df.medias.apply(
        lambda x: [i["url"].format(action="fit-in", width=870, height=653) for i in x]
    )
    df.loc[:, "created_at"] = pd.to_datetime(df.listing_createdAt)
    df.loc[:, "updated_at"] = pd.to_datetime(df.listing_updatedAt)
    df.loc[:, "usable_area"] = df.listing_usableAreas.str[0].astype(int)
    df.loc[:, "floors"] = df.listing_floors.str[0].fillna(-1)
    df.loc[:, "units_on_the_floor"] = df.listing_unitsOnTheFloor.fillna(-1)
    df.loc[:, "unit_floor"] = df.listing_unitFloor.fillna(-1)
    df.loc[:, "type_unit"] = df.listing_unitTypes.str[0]
    df.loc[:, "bedrooms"] = df.listing_bedrooms.str[0]
    df.loc[:, "bathrooms"] = df.listing_bathrooms.str[0]
    df.loc[:, "suites"] = df.listing_suites.str[0].fillna(0)
    df.loc[:, "parking_spaces"] = df.listing_parkingSpaces.str[0].fillna(0)

    df = df.dropna(subset=["bedrooms", "bathrooms"])

    df = pd.concat(
        [
            df,
            df.listing_pricingInfos.apply(
                lambda x: [
                    {
                        "price": p.get("price", 0),
                        "condo_fee": p.get("monthlyCondoFee", 0),
                    }
                    for p in x
                    if p["businessType"] == "RENTAL"
                ][0]
            )
            .apply(pd.Series)
            .astype(int),
        ],
        axis=1,
    ).assign(total_fee=lambda x: x["price"] + x["condo_fee"])

    df = df[
        [
            "url",
            "listing_title",
            "listing_description",
            "listing_publicationType",
            "media",
            "listing_address_street",
            "listing_address_streetNumber",
            "listing_address_complement",
            "listing_address_point_lat",
            "listing_address_point_lon",
            "listing_amenities",
            "usable_area",
            "floors",
            "type_unit",
            "listing_advertiserContact_phones",
            "listing_whatsappNumber",
            "bedrooms",
            "bathrooms",
            "price",
            "condo_fee",
            "total_fee",
        ]
    ]

    df.columns = [
        col.replace("listing_", "").replace("address_", "") for col in df.columns
    ]

    all_amenities = df.amenities.explode().value_counts()
    log.info(f"Todas facilidades: {all_amenities.to_dict()}")

    for amenitie in all_amenities.head(conf["max_amenities"]).index:
        df.loc[:, amenitie.lower()] = df.amenities.map(set([amenitie]).issubset)

    log.info("Buscando informações sobre metro mais próximo")

    df[["linha", "estacao", "distance"]] = (
        df[["point_lat", "point_lon"]]
        .apply(lambda x: get_min_dist(df_metro, x[0], x[1]), axis=1)
        .apply(pd.Series)
    )

    log.info("Preprocessamento finalizado")

    return df
