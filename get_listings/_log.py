import logging
from datetime import datetime
from os.path import join, dirname, abspath

basedir = abspath(join(dirname(__file__), ".."))


def setup_logger():
    """
    Classe utilizada para criar o Log
    """
    date = str(datetime.now().strftime("%Y-%m-%d"))

    logging.basicConfig(
        filename=join(basedir, "logs", f"get_listings_{date}.log"),
        format="%(asctime)s, %(module)7s, line: %(lineno)3d, %(levelname)4s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        filemode="a",
        level=logging.INFO,
    )
