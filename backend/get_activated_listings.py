import logging
import pandas as pd

from backend.timeit import timeit
from dashboard.extensions.serializer import ImovelSchema

log = logging.getLogger(__name__)
IS = ImovelSchema(many=True)


def get_activated_listings(engine, locationId, business_type, listing_type):

    with timeit(
        f"busca dos dados atualizados {listing_type=} {business_type=} {locationId=}",
        log,
        "info",
    ):
        imoveis = engine.execute(
            f"""
            SELECT i.*
            FROM imovel_ativo as a
            INNER JOIN imovel as i
            ON a.url = i.url
            WHERE
                a.listing_type = '{listing_type}'
                and a.business_type = '{business_type}'
                and a.location_id = '{locationId}'
        """
        ).all()

        return pd.DataFrame(IS.dump(imoveis))
