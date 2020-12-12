import toml
from os.path import join, dirname, abspath

def Configurations():
    dir_src = dirname(__file__)

    dir_project = abspath(join(dir_src, "..", ".."))
    dir_config = join(dir_project, "config")
    conf = toml.load(join(dir_config, "config.toml"))

    conf["dir_input"] = join(dir_project, "data", "input")
    conf["dir_webdriver"] = join(dir_config, "chromedriver")

    return conf
