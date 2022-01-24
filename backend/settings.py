from dotenv import load_dotenv, dotenv_values
from os.path import join, abspath
from toml import load
import os
import re

load_dotenv()
ENV = dotenv_values()

settings_file = abspath(join(".", "settings.toml"))
settings_file = abspath(join(__file__, "..", "..", "settings.toml"))


def read_settings():

    all_settings = load(settings_file)

    default_settings = all_settings["default"]
    env_settings = all_settings[os.environ["FLASK_ENV"]]

    settings = {**ENV, **default_settings, **env_settings}

    def format_env(value):
        if isinstance(value, str) and "@format " in value:
            value = value.replace("@format ", "").format(**ENV)

        return value

    return {k: format_env(v) for k, v in settings.items()}


settings = read_settings()
