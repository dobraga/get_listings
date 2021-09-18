import logging
import pandas as pd

from dashboard.extensions.serializer import ImovelSchema

log = logging.getLogger(__name__)
IS = ImovelSchema(many=True)


def get_activated_listings(engine, locationId, business_type, listing_type):

    log.info("Iniciando busca dos dados atualizados")

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

    log.info("Busca dos dados atualizados concluída")

    return pd.DataFrame(IS.dump(imoveis))
