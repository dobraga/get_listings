import logging
from backend.timeit import timeit


log = logging.getLogger(__name__)


def last_update(db, listing_type, business_type, locationId):
    with timeit(
        f"Busca data última atualização {listing_type=} {business_type=} {locationId=}",
        log,
    ):
        return db.engine.execute(
            f"""
            SELECT max(updated_date)
            FROM imovel_ativo
            WHERE
                listing_type = '{listing_type}'
                and business_type = '{business_type}'
                and location_id = '{locationId}'
            """
        ).scalar()


def clean_imoveis_ativos(db, listing_type, business_type, locationId):
    with timeit(
        f"Limpando dados dos imóveis ativos {listing_type=} {business_type=} {locationId=}",
        log,
    ):
        db.engine.execute(
            f"""
            DELETE FROM imovel_ativo
            WHERE
                listing_type = '{listing_type}'
                and business_type = '{business_type}'
                and location_id = '{locationId}'
            """
        )
