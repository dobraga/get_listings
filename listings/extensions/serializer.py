from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from listings.models import Imovel, Metro

ma = Marshmallow()


def init_app(app):
    ma.init_app(app)
    app.ma = ma


class ImovelSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Imovel
        load_instance = True
        transient = True
        fields = (
            "title",
            "url",
            "images",
            "neighborhood",
            "locationId",
            "state",
            "city",
            "zone",
            "business_type",
            "listing_type",
            "usable_area",
            "floors",
            "type_unit",
            "bedrooms",
            "bathrooms",
            "suites",
            "parking_spaces",
            "amenities",
            "address",
            "address_lat",
            "address_lon",
            "price",
            "condo_fee",
            "total_fee",
            "total_fee_predict",
            "created_date",
            "estacao",
            "distance",
            "created_date",
            "updated_date",
            "total_fee_predict",
        )


class MetroSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Metro
        load_instance = True
        transient = True
        fields = ("linha", "estacao", "lat", "lng")
