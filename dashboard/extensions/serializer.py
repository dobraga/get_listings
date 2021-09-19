from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from dashboard.models import Imovel, Metro

ma = Marshmallow()


def init_app(app):
    ma.init_app(app)
    app.ma = ma
    return app


class ImovelSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Imovel
        load_instance = True
        transient = True
        fields = (
            "title",
            "url",
            "business_type",
            "listing_type",
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
            "lat_metro",
            "lon_metro",
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
