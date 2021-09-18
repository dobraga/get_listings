import mlflow
import logging
from joblib import dump
from os.path import join, abspath

from modeling.data import get_data
from modeling.optimizer import create_model, scorer

log = logging.getLogger(__name__)

root_dir = "."
root_dir = join(__file__, "..", "..")
file_model = abspath(join(root_dir, "data", "model.pkl"))
log.info(f"Saving model in {file_model}")


X, y = get_data()


best_model = (
    mlflow.search_runs(experiment_ids="1")
    .query("`metrics.fit_time` < 1000 and `metrics.score_time` < 0.1")
    .sort_values("metrics.test_mae", ascending=False)
    .head(1)
)

metrics = best_model[[col for col in best_model.columns if "metrics" in col]]
metrics.columns = [col.replace("metrics.", "") for col in metrics.columns]
metrics = metrics.to_dict("records")[0]


params = best_model[[col for col in best_model.columns if "params" in col]]
params.columns = [col.replace("params.", "") for col in params.columns]
params = params.T.dropna().T.to_dict("records")[0]


def try_eval(value):
    try:
        return eval(value)
    except:
        return value


params = {p: try_eval(v) for p, v in params.items()}

model = create_model(**params)
model.fit(X, y)

y_pred = model.predict(X)


final_metric = {n: s._score_func(y, y_pred) for n, s in scorer.items()}

log.info(f"{metrics} | {final_metric}")

dump(model, file_model)

log.info("Model saved")
