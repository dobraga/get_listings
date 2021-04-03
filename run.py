from get_listings._config import Configurations
from get_listings.preprocess import preprocess
from get_listings.request import run_request
from get_listings._log import setup_logger
from get_listings.model import run_model
from get_listings import metro
import pandas as pd


def run(local=None):
    setup_logger()
    conf = Configurations()

    data, local, local_file, new_file = run_request(conf, local)

    if new_file:
        metro.run(conf)
        df = preprocess(conf, data)
        df = run_model(df, local_file)
    else:
        df = pd.read_parquet(
            local_file.replace(".jsonl", ".parquet").replace("input", "output")
        )

    return df, local


if __name__ == "__main__":
    run()
