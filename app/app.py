from flask import Flask
from app.views import home, table, map, api


app = Flask(__name__)

home.init_app(app)
table.init_app(app)
map.init_app(app)
api.init_app(app)
