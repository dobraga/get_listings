import toml
from os.path import join, dirname, abspath

def Configurations():
    dir_src = dirname(__file__)

    conf = toml.load(join(dir_src, "config.toml"))
    
    dir_project = abspath(join(dir_src, "..", ".."))
    conf["dir_input"] = join(dir_project, "data", "input")

    return conf
