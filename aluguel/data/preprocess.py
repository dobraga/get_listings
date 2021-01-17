from geopy.distance import distance
from os.path import join
import pandas as pd


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


def preprocess(conf, file="imoveis.jsonlines", file_metro="metro.jsonlines"):
    df_metro = pd.read_json(join(conf["dir_input"], file_metro), lines=True)
    df_metro = df_metro.drop_duplicates()

    df = (
        pd.read_json(join(conf["dir_input"], file), lines=True)
        .groupby("id")
        .last()
        .reset_index()
    )

    df = df[(df.tipo == "Aluguel") & (~df.quartos.isna())]

    df["vagas"] = df["vagas"].fillna(0)

    df["desc"] = df.desc.str.replace("\n", "")

    cols_num = ["lat", "lng", "condominio"]
    df[cols_num] = df[cols_num].apply(pd.to_numeric)

    df["preco_total"] = df["preco"] + df["condominio"]

    df[["linha", "estacao", "distance"]] = (
        df[["lat", "lng"]]
        .apply(lambda x: get_min_dist(df_metro, x[0], x[1]), axis=1)
        .apply(pd.Series)
    )

    df.to_csv(join(conf["dir_output"], "apartamentos.csv"), index=None)

    return df
