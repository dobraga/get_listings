import logging
import pandas as pd
from datetime import datetime


from backend.settings import settings
from backend import create_or_update_listings, get_activated_listings, bd


log = logging.getLogger(__name__)


def get_listings(
    locationId: str,
    neighborhood: str,
    state: str,
    city: str,
    stateAcronym: str,
    zone: str,
    business_type: str,
    listing_type: str,
    db,
    force=False,
    **kwargs,
) -> pd.DataFrame:

    force_update = settings.get("FORCE_UPDATE", False) or force

    # Para dados que já foram atualizados no dia da consulta, apenas retorna os dados
    last_update = bd.last_update(db, listing_type, business_type, locationId)

    # Caso ja tenha dados atualizados do dia corrente
    if last_update:
        log.info(f'Última atualização em "{last_update}"')
        if not force_update and last_update.date() == datetime.today().date():
            return get_activated_listings.get_activated_listings(
                db, locationId, business_type, listing_type
            )

    create_or_update_listings.create_or_update_listings(
        locationId,
        neighborhood,
        state,
        stateAcronym,
        city,
        zone,
        business_type,
        listing_type,
        db,
    )

    return get_activated_listings.get_activated_listings(
        db, locationId, business_type, listing_type
    )
