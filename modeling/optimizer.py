import optuna
import logging
import numpy as np
import pandas as pd
import xgboost as xgb
import lightgbm as lgb
from sqlalchemy import create_engine
from mlflow.tracking import MlflowClient
from mlflow.utils.mlflow_tags import MLFLOW_PARENT_RUN_ID
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import cross_validate
from sklearn.compose import TransformedTargetRegressor
from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor
from sklearn.metrics import (
    make_scorer,
    mean_squared_error as mse,
    mean_absolute_error as mae,
    mean_absolute_percentage_error as mape,
)

from backend.settings import settings
from backend.preprocess import preprocess

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
log = logging.getLogger(__name__)

df = pd.read_sql(
    """
        select url, neighborhood, usable_area, floors, type_unit, bedrooms, bathrooms, suites, parking_spaces,
        amenities, address_lat, address_lon, total_fee, estacao, distance, created_date, updated_date
        from imovel
    """,
    engine,
)
log.info("Data read finished")
X, y = preprocess(df)
log.info("Preprocess data finished")


def create_model(model, transformer_x, transformer_y, **kwargs):
    model = {
        "ExtraTreesRegressor": ExtraTreesRegressor,
        "RandomForestRegressor": RandomForestRegressor,
        "LGBMRegressor": lgb.LGBMRegressor,
        "XGBRegressor": xgb.XGBRegressor,
    }[model]

    model = model(**kwargs)
    if transformer_x:
        model = make_pipeline(MinMaxScaler(), model)

    if transformer_y:
        model = TransformedTargetRegressor(model, func=np.log1p, inverse_func=np.expm1)

    return model


##################
# Define Métrica #
##################


def rmse(y_true, y_pred):
    return np.sqrt(mse(y_true, y_pred))


scorer = {
    "mape": make_scorer(mape, greater_is_better=False),
    "rmse": make_scorer(rmse, greater_is_better=False),
    "mae": make_scorer(mae, greater_is_better=False),
}


######################
# Executa otimização #
######################

if __name__ == "__main__":
    ####################
    # Configura MLFlow #
    ####################

    # https://simonhessner.de/mlflow-optuna-parallel-hyper-parameter-optimization-and-logging/

    client = MlflowClient()
    experiment_name = "opt_rmse"

    # try:
    experiment = client.create_experiment(experiment_name)
    # except:
    # experiment = client.get_experiment_by_name(experiment_name).experiment_id

    study_run = client.create_run(experiment_id=experiment)
    study_run_id = study_run.info.run_id

    ####################
    # Configura Optuna #
    ####################

    # def get_objective(parent_run_id):
    #     # get an objective function for optuna that creates nested MLFlow runs

    #     def objective(trial):
    #         trial_run = client.create_run(
    #             experiment_id=experiment, tags={MLFLOW_PARENT_RUN_ID: parent_run_id}
    #         )

    #         name_model = trial.suggest_categorical(
    #             "model",
    #             [
    #                 "LGBMRegressor",
    #                 "XGBRegressor",
    #                 "RandomForestRegressor",
    #                 "ExtraTreesRegressor",
    #             ],
    #         )

    #         if name_model == "ExtraTreesRegressor":
    #             param = {
    #                 "random_state": 20,
    #                 "n_estimators": trial.suggest_int("n_estimators", 10, 500),
    #                 "max_depth": trial.suggest_int("max_depth", 1, 10),
    #                 "max_features": trial.suggest_categorical(
    #                     "max_features", ["auto", "sqrt", "log2"]
    #                 ),
    #                 "min_samples_leaf": trial.suggest_int("min_samples_leaf", 1, 10),
    #                 "min_samples_split": trial.suggest_int("min_samples_split", 2, 10),
    #                 "criterion": trial.suggest_categorical("criterion", ["mse", "mae"]),
    #                 "bootstrap": trial.suggest_categorical("bootstrap", [True, False]),
    #             }

    #         elif name_model == "RandomForestRegressor":
    #             param = {
    #                 "random_state": 20,
    #                 "n_estimators": trial.suggest_int("n_estimators", 10, 500),
    #                 "max_depth": trial.suggest_int("max_depth", 1, 10),
    #                 "max_features": trial.suggest_categorical(
    #                     "max_features", ["auto", "sqrt", "log2"]
    #                 ),
    #                 "min_samples_leaf": trial.suggest_int("min_samples_leaf", 1, 10),
    #                 "min_samples_split": trial.suggest_int("min_samples_split", 2, 10),
    #                 "criterion": trial.suggest_categorical("criterion", ["mse", "mae"]),
    #                 "bootstrap": trial.suggest_categorical("bootstrap", [True, False]),
    #             }

    #         elif name_model == "LGBMRegressor":
    #             param = {
    #                 "random_state": 20,
    #                 "n_estimators": trial.suggest_int("n_estimators", 10, 500),
    #                 "max_depth": trial.suggest_int("max_depth", 1, 10),
    #                 "colsample_bytree": trial.suggest_float(
    #                     "colsample_bytree", 0.1, 0.9
    #                 ),
    #                 "subsample": trial.suggest_float("subsample", 0.6, 1.0),
    #                 "num_leaves": trial.suggest_int("num_leaves", 2, 90),
    #                 "min_split_gain": trial.suggest_float("min_split_gain", 0.001, 0.1),
    #                 "reg_alpha": trial.suggest_float("reg_alpha", 0, 1),
    #                 "reg_lambda": trial.suggest_float("reg_lambda", 0, 1),
    #                 "min_child_weight": trial.suggest_int("min_child_weight", 5, 50),
    #                 "learning_rate": trial.suggest_float("learning_rate", 1e-5, 5e-1),
    #             }

    #         elif name_model == "XGBRegressor":
    #             param = {
    #                 "random_state": 20,
    #                 "n_estimators": trial.suggest_int("n_estimators", 10, 500),
    #                 "max_depth": trial.suggest_int("max_depth", 1, 10),
    #                 "colsample_bytree": trial.suggest_float(
    #                     "colsample_bytree", 0.1, 0.9
    #                 ),
    #                 "subsample": trial.suggest_float("subsample", 0.6, 1.0),
    #                 "reg_alpha": trial.suggest_float("reg_alpha", 0, 1),
    #                 "reg_lambda": trial.suggest_float("reg_lambda", 0, 1),
    #                 "min_child_weight": trial.suggest_int("min_child_weight", 5, 50),
    #                 "learning_rate": trial.suggest_float("learning_rate", 1e-5, 5e-1),
    #             }

    #         transformer_x = trial.suggest_categorical("transformer_x", [True, False])
    #         transformer_y = trial.suggest_categorical("transformer_y", [True, False])

    #         model = create_model(name_model, transformer_x, transformer_y, **param)

    #         # Log dos parâmetros
    #         client.log_param(trial_run.info.run_id, "model", name_model)
    #         client.log_param(trial_run.info.run_id, "transformer_x", transformer_x)
    #         client.log_param(trial_run.info.run_id, "transformer_y", transformer_y)
    #         [client.log_param(trial_run.info.run_id, k, v) for k, v in param.items()]

    #         # Realiza validação cruzada e faz log da métricas
    #         metrics = cross_validate(
    #             model, X.fillna(-1), y, cv=5, scoring=scorer, n_jobs=-1
    #         )

    #         for metric_name, metric_values in metrics.items():
    #             [
    #                 client.log_metric(trial_run.info.run_id, metric_name, m)
    #                 for m in metric_values
    #             ]

    #         return np.median(metrics["test_rmse"])

    #     return objective

    # study = optuna.create_study(
    #     study_name="optuna_opt",
    #     direction="minimize",
    #     load_if_exists=True,
    #     storage="sqlite:///data/opt_rmse.db",
    # )

    # study.optimize(get_objective(study_run_id), n_trials=1000)
