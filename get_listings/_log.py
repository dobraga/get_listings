import logging
from os.path import join, dirname, abspath

basedir = abspath(join(dirname(__file__), ".."))


def setup_logger(file_name: str = "get_listings.log"):
    """
    Classe utilizada para criar o Log
    """
    logging.basicConfig(
        filename=join(basedir, "logs", file_name),
        format="%(asctime)s, %(module)7s, line: %(lineno)3d, %(levelname)4s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        filemode="a",
        level=logging.INFO,
    )
