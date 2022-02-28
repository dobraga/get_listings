from datetime import datetime
import pandas as pd
import numpy as np
import logging

from backend.timeit import timeit

log = logging.getLogger(__name__)


def onehot(values: pd.Series, options: list, prefix: str = None) -> pd.Series:
    index = values.index
    oh = pd.get_dummies(
        pd.Categorical(values, categories=options, ordered=False), prefix=prefix
    )
    oh.index = index
    oh.columns = map(lambda x: x.replace(" ", "_"), oh.columns)
    return oh


def preprocess(df: pd.DataFrame) -> tuple:
    with timeit("Preprocessamento", log):
        df = df.copy()

        df["neighborhood"] = df["neighborhood"].map(
            df.groupby("neighborhood")["total_fee"].median()
        )

        y = df.pop("total_fee")

        X = df[
            [
                "neighborhood",
                "url",
                "usable_area",
                "floors",
                "type_unit",
                "bedrooms",
                "bathrooms",
                "suites",
                "parking_spaces",
                "amenities",
                "address_lat",
                "address_lon",
                "estacao",
                "distance",
                "created_date",
                "updated_date",
            ]
        ].set_index("url")

        #
        # Colunas Numéricas
        #
        numeric_columns = [
            "usable_area",
            "floors",
            "bedrooms",
            "bathrooms",
            "suites",
            "parking_spaces",
            "address_lat",
            "address_lon",
            "distance",
        ]
        X[numeric_columns] = X[numeric_columns].astype(float).fillna(-999)

        #
        # Transforma datas de criação e atualização em features
        #
        X["qtd_days_created"] = (
            (
                (datetime.now() - pd.to_datetime(X["created_date"]))
                / np.timedelta64(1, "D")
            )
            .round()
            .fillna(-1)
            .astype(int)
        )
        X["qtd_days_updated"] = (
            (
                (datetime.now() - pd.to_datetime(X["updated_date"]))
                / np.timedelta64(1, "D")
            )
            .round()
            .fillna(-1)
            .astype(int)
        )

        #
        # Transforma colunas não numéricas
        #

        # Type Unit
        valid_type_unit = ["APARTMENT", "HOME", "CONDOMINIUM", "PENTHOUSE", "FLAT"]
        X.loc[~X.type_unit.isin(valid_type_unit), "type_unit"] = "OTHERS"
        dummies_type_units = onehot(
            X.type_unit, valid_type_unit + ["OTHERS"], "type_unit"
        )
        X[dummies_type_units.columns] = dummies_type_units.values

        # Estação de trem/metrô
        estacoes_validas = [
            "Estação_Jardim_Oceânico",
            "Estação_Uruguai",
            "Estação_Botafogo/Coca-Cola",
            "Estação_Afonso_Pena",
            "Estação_Saens_Peña",
            "Estação_Flamengo",
            "Estação_São_Francisco_Xavier_(Metrô_Rio)",
            "Estação_Madureira",
        ]
        # estacoes = X.loc[X.estacao != "", "estacao"].value_counts(normalize=True)
        # estacoes_validas = list(estacoes[estacoes > 0.05].index)
        X.loc[~X.estacao.isin(estacoes_validas), "estacao"] = "OTHERS"
        dummies_estacoes = onehot(X.type_unit, estacoes_validas + ["OTHERS"], "estação")
        X[dummies_estacoes.columns] = dummies_estacoes.values

        # Amenities
        valid_amenities = [
            "ELEVATOR",
            "POOL",
            "BARBECUE_GRILL",
            "PARTY_HALL",
            "PLAYGROUND",
            "GATED_COMMUNITY",
            "BALCONY",
            "INTERCOM",
            "KITCHEN_CABINETS",
            "GYM",
            "SAUNA",
            "FURNISHED",
            "SPORTS_COURT",
        ]
        amenities = X.amenities.explode()
        amenities[~amenities.isin([valid_amenities])] = "OTHERS"
        dummies_amenities = (
            onehot(amenities, valid_amenities, "amenity").groupby(level=0).max()
        )
        X[dummies_amenities.columns] = dummies_amenities.values

        # Remove colunas
        X = X.drop(
            columns=[
                "type_unit",
                "estacao",
                "created_date",
                "updated_date",
                "amenities",
            ]
        )

        return X, y
