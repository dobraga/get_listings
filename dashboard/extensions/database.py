from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dash import Dash

db = SQLAlchemy()


def init_app(app: Dash) -> Dash:
    server = app.server
    server.db = db

    db.init_app(server)
    Migrate(server, db)

    return app
