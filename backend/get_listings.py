import logging
import pandas as pd
from datetime import datetime

from backend import update_predict, get_activated_listings, extract_new_data, bd, metro
from backend.settings import settings

log = logging.getLogger(__name__)


def get_listings(
    neighborhood: str,
    locationId: str,
    state: str,
    stateAcronym: str,
    city: str,
    zone: str,
    business_type: str,
    listing_type: str,
    db,
    **kwargs,
) -> pd.DataFrame:

    force_update = settings.get("force_update", False)

    last_update = bd.last_update(db, listing_type, business_type, locationId)

    # Caso não tenha dados atualizados do dia corrente ou seja uma atualização forçada
    if force_update or not last_update or last_update.date() != datetime.today().date():
        extract_new_data.extract_new_data(
            last_update,
            force_update,
            neighborhood,
            locationId,
            state,
            city,
            zone,
            business_type,
            listing_type,
            metro.get_metro(stateAcronym.lower(), db),
            db,
            **kwargs,
        )

        update_predict.update_predict(db, locationId, business_type, listing_type)

    return get_activated_listings.get_activated_listings(
        db.engine, locationId, business_type, listing_type
    )
