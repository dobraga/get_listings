import pandas as pd
from geopy.distance import distance
from os.path import join, abspath, dirname

dir_src = dirname(__file__)
dir_project = abspath(join(dir_src, ".."))
dir_input = join(dir_project, "data", "input")
dir_output = join(dir_project, "data", "output")

df_metro = pd.read_json(join(dir_input, "metro.jsonlines"), lines=True)


def get_min_dist(lat, lng):
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


def clean(sites=["zap", "vivareal"]):
    dfs = []
    for site in sites:
        dfs.append(pd.read_json(join(dir_input, f"{site}.jsonlines"), lines=True))

    df = pd.concat(dfs)

    df = df[df.tipo.str.contains("lug")]

    df[["lat", "lng", "condominio"]] = df[["lat", "lng", "condominio"]].apply(
        pd.to_numeric
    )

    # df = df[~df.lat.isna()]

    df["preco_total"] = df["preco"] + df["condominio"]

    df[["linha", "estacao", "distance"]] = (
        df[["lat", "lng"]]
        .apply(lambda x: get_min_dist(x[0], x[1]), axis=1)
        .apply(pd.Series)
    )

    return df


if __name__ == "__main__":
    df = clean()
    df.to_csv(join(dir_output, "apartamentos.csv"), index=None)
