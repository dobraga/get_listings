from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dash import Dash

db = SQLAlchemy()


def init_app(app: Dash) -> Dash:
    db.init_app(app.server)
    Migrate(app.server, db)
    app.db = db

    return app