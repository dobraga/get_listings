from flask import Flask

from .extensions import conf, database, serializer, logger
from .views import home, table, map


def create_app():
    app = Flask(__name__)

    home.init_app(app)
    table.init_app(app)
    map.init_app(app)

    logger.init_app(app)
    conf.init_app(app)
    database.init_app(app)
    serializer.init_app(app)
    app.logger.info("App inicializado")

    return app
