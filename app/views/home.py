from get_listings.location import list_locations

from wtforms import StringField, SubmitField, BooleanField, SelectField
from flask import render_template, url_for, redirect
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm


class homepage(FlaskForm):
    local = StringField("local", validators=[DataRequired()])
    query = StringField("query")
    search = SubmitField("Search")
    submit_table = SubmitField("Table")
    submit_map = SubmitField("Map")

    tp_contrato = SelectField(
        "Tipo Contrato", choices=[("RENTAL", "Aluguel"), ("SALE", "Compra")]
    )
    tp_listings = SelectField(
        "Tipo Imovel", choices=[("USED", "Usando"), ("DEVELOPMENT", "Novo")]
    )

    checkbox0 = BooleanField("checkbox0")
    checkbox1 = BooleanField("checkbox1")
    checkbox2 = BooleanField("checkbox2")
    checkbox3 = BooleanField("checkbox3")
    checkbox4 = BooleanField("checkbox4")
    checkbox5 = BooleanField("checkbox5")


def init_app(app):
    @app.route("/", methods=["GET", "POST"])
    def home():
        form = homepage(meta={"csrf": False})

        if form.validate_on_submit():
            if form.search.data:
                locations = list_locations(form.local.data)
                return render_template("home.html", form=form, locations=locations)

            else:
                locations = list_locations(form.local.data)
                local = {}

                for i, checkbox in enumerate(
                    [
                        form.checkbox0.data,
                        form.checkbox1.data,
                        form.checkbox2.data,
                        form.checkbox3.data,
                        form.checkbox4.data,
                        form.checkbox5.data,
                    ]
                ):
                    if checkbox:
                        local = locations[i]

                if not local:
                    return render_template("home.html", form=form, **local)

                elif form.submit_table.data:
                    url = url_for(
                        "table",
                        query=form.query.data,
                        tp_contrato=form.tp_contrato.data,
                        tp_listings=form.tp_listings.data,
                        **local
                    )

                elif form.submit_map.data:
                    url = url_for(
                        "map",
                        query=form.query.data,
                        tp_contrato=form.tp_contrato.data,
                        tp_listings=form.tp_listings.data,
                        **local
                    )

                return redirect(url)

        return render_template("home.html", form=form, locations=[])
