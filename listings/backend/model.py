from sklearn.metrics import (
    mean_absolute_error as mae,
    mean_absolute_percentage_error as mape,
    mean_squared_error as mse,
)
from sklearn.model_selection import KFold
import lightgbm as lgb
import pandas as pd
import numpy as np
import logging

log = logging.getLogger(__name__)


class Model:
    def __init__(self, model):
        self.base_model = model

    def fit_predict(self, X, y, n_folds=5, clip=True, prep=np.log1p, posp=np.expm1):
        y_predict = np.zeros(y.shape[0])

        for train_index, test_index in KFold(n_splits=n_folds).split(X):
            X_train, X_test = X.iloc[train_index], X.iloc[test_index]
            y_train = y[train_index]

            if clip:
                qt = np.quantile(y_train, [0.99, 1])
                y_train = np.clip(y_train, 0, qt[0])

            model = self.base_model.fit(X_train, prep(y_train))
            y_predict[test_index] = posp(model.predict(X_test))

        log.info(
            {
                metric.__name__: round(metric(y, y_predict), 4)
                for metric in [mse, mae, mape]
            }
        )

        return y_predict


def run_model(df):
    if df.shape[0] == 0:
        return df

    y = df.total_fee.values
    X = df.drop(
        columns=[
            "url",
            "title",
            "description",
            "media",
            "street",
            "streetNumber",
            "complement",
            "amenities",
            "advertiserContact_phones",
            "whatsappNumber",
            "price",
            "condo_fee",
            "total_fee",
        ]
    )
    X = pd.get_dummies(X).fillna(-1)

    df = df.assign(
        pred=Model(lgb.LGBMRegressor()).fit_predict(X, y),
        error=lambda x: x["total_fee"] - x["pred"],
    ).sort_values("error", ascending=True)

    return df
