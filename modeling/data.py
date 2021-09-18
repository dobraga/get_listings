from backend.preprocess import preprocess

import pandas as pd
from sqlalchemy import create_engine


engine = create_engine("postgresql://postgres:postgres@localhost:15432/listing")


def get_data():

    df_original = pd.read_sql(
        """
        select url, neighborhood, usable_area, floors, type_unit, bedrooms, bathrooms, suites, parking_spaces,
        amenities, address_lat, address_lon, total_fee, estacao, distance, created_date, updated_date
        from imovel
    """,
        engine,
    )

    return preprocess(df_original)
