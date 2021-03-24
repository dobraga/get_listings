from flask import Flask, render_template
import pandas as pd

app = Flask(__name__)


@app.route("/")
def index():
    df = pd.read_parquet("./data/output/listings_modeled.parquet")
    return render_template("index.html", df=df)
