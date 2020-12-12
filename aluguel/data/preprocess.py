import re
import joblib
import pandas as pd
from geopy.distance import distance
from scipy.sparse import hstack, save_npz
from os.path import join, abspath, dirname

dir_src = dirname(__file__)
dir_project = abspath(join(dir_src, "..", ".."))
dir_input = join(dir_project, "data", "input")
dir_output = join(dir_project, "data", "output")
dir_objects = join(dir_project, "data", "objects")


def get_min_dist(df_metro, lat, lng):
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


def clean(file="imoveis.jsonlines", json=None, file_metro="metro.jsonlines"):
    df_metro = pd.read_json(join(dir_input, file_metro), lines=True).drop_duplicates()

    if json:
        df = pd.DataFrame([json])
    else:
        df = (
            pd.read_json(join(dir_input, file), lines=True)
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

    return df


def preprocess(file="imoveis.jsonlines", json=None, file_metro="metro.jsonlines"):
    df = clean(file, json, file_metro)
    if not json:
        df.to_csv(join(dir_output, "apartamentos.csv"), index=None)

    tc = joblib.load(join(dir_objects, "ajusta_desc.pkl"))
    oh = joblib.load(join(dir_objects, "onehot.pkl"))
    tfidf = joblib.load(join(dir_objects, "tfidf.pkl"))

    df = df[
        [
            "metragem",
            "quartos",
            "banheiros",
            "vagas",
            "lat",
            "lng",
            "desc",
            "linha",
            "estacao",
            "distance",
        ]
    ].dropna()

    def ordinal_encoder(df, oh):
        X_encode = pd.DataFrame(oh.transform(df[["linha", "estacao"]]))
        X_encode.columns = oh.get_feature_names(["fl", "fl"])
        X_encode = X_encode.set_index(df.index)
        X_encode = pd.concat([df.drop(columns=["linha", "estacao"]), X_encode], axis=1)
        return X_encode

    df = tc.transform(df)
    df = ordinal_encoder(df, oh)
    df = hstack([tfidf.transform(df.desc), df.drop(columns="desc")])

    if not json:
        save_npz(join(dir_output, "apartamentos.npz"), df)

    return df


if __name__ == "__main__":
    df = preprocess()
