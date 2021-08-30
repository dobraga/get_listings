from sklearn.metrics import mean_absolute_error as mae, mean_squared_error as mse
from sklearn.compose import TransformedTargetRegressor
from sklearn.model_selection import cross_val_predict
from datetime import datetime
import lightgbm as lgb
import pandas as pd
import numpy as np
import logging

log = logging.getLogger(__name__)


def rmse(y_true, y_pred):
    return np.sqrt(mse(y_true, y_pred))


metrics = [mae, rmse]


def preprocess(df: pd.DataFrame) -> tuple:
    log.info("Preprocessamento para modelagem iniciado")
    df = df.copy()

    X = df[
        [
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
    y = df.total_fee.values

    # Transforma datas de criação e atualização em features
    X["qtd_days_created"] = (
        ((datetime.now() - pd.to_datetime(X["created_date"])) / np.timedelta64(1, "D"))
        .round()
        .astype(int)
    )
    X["qtd_days_updated"] = (
        ((datetime.now() - pd.to_datetime(X["updated_date"])) / np.timedelta64(1, "D"))
        .round()
        .astype(int)
    )

    # Transforma colunas não numéricas
    X.loc[
        ~X.type_unit.isin(["APARTMENT", "HOME", "CONDOMINIUM", "PENTHOUSE", "FLAT"]),
        "type_unit",
    ] = "OTHERS"

    estacoes = X.loc[X.estacao != "", "estacao"].value_counts(normalize=True)
    estacoes_validas = list(estacoes[estacoes > 0.05].index) + [""]
    X.loc[~X.estacao.isin(estacoes_validas), "estacao"] = "OTHERS"

    # dummies
    dummies = pd.get_dummies(X[["type_unit", "estacao"]])
    X[dummies.columns] = dummies.values

    # amenities
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
    amenities = pd.get_dummies(amenities).groupby(level=0).max()
    X[amenities.columns] = amenities.values
    X = X.drop(
        columns=["type_unit", "estacao", "created_date", "updated_date", "amenities"]
    )

    log.info("Preprocessamento para modelagem finalizado")

    return X, y


def predict(df: pd.DataFrame) -> np.ndarray:
    X, y = preprocess(df)

    log.info("Modelagem iniciada")

    model = lgb.LGBMRegressor()
    model = TransformedTargetRegressor(model, func=np.log1p, inverse_func=np.expm1)

    predict = cross_val_predict(model, X, y, n_jobs=-1)

    m = {m.__name__: m(y, predict) for m in metrics}
    log.info(f"Using {model} with metrics {m}")

    log.info("Modelagem finalizada")

    return predict
