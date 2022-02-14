from pprint import pprint
from dynaconf import Dynaconf

settings = Dynaconf(
    settings_files=["settings.toml"],
    env_switcher="FLASK_ENV",
    environments=True,
    load_dotenv=True,
)


pprint(dict(settings))
