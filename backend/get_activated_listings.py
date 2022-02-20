import logging
from venv import create
import pandas as pd
from sqlalchemy import select, and_

from backend.timeit import timeit
from dashboard.models import Imovel, ImovelAtivo
from dashboard.extensions.serializer import ImovelSchema

log = logging.getLogger(__name__)
IS = ImovelSchema(many=True)


def get_activated_listings(db, locationId, business_type, listing_type):

    with timeit(
        f"busca dos dados atualizados {listing_type=} {business_type=} {locationId=}",
        log,
        "info",
    ):
        with db.engine.connect() as c:
            imoveis = c.execute(
                select(Imovel)
                .join(ImovelAtivo, Imovel.url == ImovelAtivo.url)
                .where(
                    and_(
                        Imovel.listing_type == listing_type,
                        Imovel.business_type == business_type,
                        Imovel.location_id == locationId,
                    )
                )
            ).all()

        return pd.DataFrame(IS.dump(imoveis))


if __name__ == "__main__":
    from sqlalchemy import create_engine

    from backend.settings import settings

    engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)

    df = get_activated_listings(
        engine,
        "BR>Rio de Janeiro>NULL>Rio de Janeiro>Zona Norte>Tijuca",
        "RENTAL",
        "USED",
    )

    df[["title", "url"]].apply(lambda x: f"![{x[0]}]({x[1]})", axis=1)
