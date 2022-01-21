from dynaconf import Dynaconf
from dotenv import load_dotenv

load_dotenv()
settings = Dynaconf(settings_files=["settings.toml"], environments=True)
