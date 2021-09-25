from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from sqlalchemy.sql import func
from datetime import datetime
from sqlalchemy import JSON
import uuid

from dashboard.extensions.database import db


class Imovel(db.Model):
    __tablename__ = "imovel"
    url = db.Column(db.String(), nullable=False, primary_key=True)

    neighborhood = db.Column(db.String(), nullable=False)
    location_id = db.Column(db.String(), nullable=False)
    state = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(), nullable=False)
    zone = db.Column(db.String(), nullable=False)
    business_type = db.Column(db.String(), nullable=False)
    listing_type = db.Column(db.String(), nullable=False)

    raw = db.Column(JSON(), nullable=False)

    title = db.Column(db.String())
    usable_area = db.Column(db.Float())
    floors = db.Column(db.Integer())
    type_unit = db.Column(db.String())
    bedrooms = db.Column(db.Integer())
    bathrooms = db.Column(db.Integer())
    suites = db.Column(db.Integer())
    parking_spaces = db.Column(db.Integer())
    amenities = db.Column(db.ARRAY(db.String()))
    images = db.Column(db.ARRAY(db.String()))

    address = db.Column(db.String())
    address_lat = db.Column(db.Float())
    address_lon = db.Column(db.Float())

    price = db.Column(db.Float())
    condo_fee = db.Column(db.Float())
    total_fee = db.Column(db.Float())

    linha = db.Column(db.String())
    estacao = db.Column(db.String())
    lat_metro = db.Column(db.Float())
    lon_metro = db.Column(db.Float())
    distance = db.Column(db.Float())

    created_date = db.Column(db.DateTime(timezone=False))
    updated_date = db.Column(db.DateTime(timezone=False))

    total_fee_predict = db.Column(db.Float())

    created = db.Column(TIMESTAMP, server_default=func.now())
    updated = db.Column(
        TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp()
    )


class ImovelAtivo(db.Model):
    __tablename__ = "imovel_ativo"

    url = db.Column(db.String(), db.ForeignKey("imovel.url"), primary_key=True)
    location_id = db.Column(db.String(), nullable=False)
    business_type = db.Column(db.String(), nullable=False)
    listing_type = db.Column(db.String(), nullable=False)

    updated_date = db.Column(db.DateTime(timezone=False), default=datetime.utcnow())


class Metro(db.Model):
    __tablename__ = "metro"
    id = db.Column(
        UUID(as_uuid=True), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    uf = db.Column(db.String, nullable=False)
    linha = db.Column(db.String, nullable=False)
    estacao = db.Column(db.String, nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)
    url = db.Column(db.String, nullable=False)
