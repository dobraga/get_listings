import toml
import logging
from os.path import join, dirname, abspath

log = logging.getLogger(__name__)


def Configurations():
    dir_src = dirname(__file__)
    dir_project = abspath(join(dir_src, ".."))

    conf = toml.load(join(dir_project, "config.toml"))
    conf["dir_input"] = join(dir_project, "data", "input")
    conf["dir_output"] = join(dir_project, "data", "output")

    log.info("Settings loaded")

    return conf
