import sys
import logging
from os.path import join, dirname, abspath

basedir = abspath(join(dirname(__file__), "..", ".."))

def Logger(file_name:str, level:str="INFO") -> logging.Logger:
    """
    Classe utilizada para criar o Log
    """
    formatter = logging.Formatter(
        fmt="%(asctime)s: line: %(lineno)3d: %(levelname)8s : %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    if level == "DEBUG":
        level = logging.DEBUG
    elif level == "ERROR":
        level = logging.ERROR
    elif level == "WARNING":
        level = logging.WARNING
    else:
        level = logging.INFO

    logging.basicConfig(
        filename=join(basedir, "logs", file_name),
        format="%(asctime)s, %(module)7s, line: %(lineno)3d, %(levelname)4s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        filemode="a",
        level=level,
    )
    log_obj = logging.getLogger()
    log_obj.setLevel(level)

    screen_handler = logging.StreamHandler(
        stream=sys.stdout
    )
    screen_handler.setFormatter(formatter)
    logging.getLogger().addHandler(screen_handler)

    return log_obj

