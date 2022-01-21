import logging
import pandas as pd
from datetime import datetime
from joblib import Parallel, delayed
from concurrent.futures import ProcessPoolExecutor, as_completed

from backend.timeit import timeit
from backend import clean_data, request_page, update_predict, get_activated_listings, bd
from dashboard.models import Imovel, ImovelAtivo
from backend.settings import settings

log = logging.getLogger(__name__)


def get_listings(
    neighborhood: str,
    locationId: str,
    state: str,
    city: str,
    zone: str,
    business_type: str,
    listing_type: str,
    df_metro: pd.DataFrame,
    db,
    **kwargs,
) -> pd.DataFrame:

    force_update = settings.get("FORCE_UPDATE", False)

    # Para dados que já foram atualizados no dia da consulta, apenas retorna os dados
    last_update = bd.last_update(db, listing_type, business_type, locationId)

    # Caso ja tenha dados atualizados do dia corrente
    if (
        not force_update
        and last_update
        and last_update.date() == datetime.today().date()
    ):
        return get_activated_listings(
            bd.engine, locationId, business_type, listing_type
        )

    # Caso contrário, limpa dados dos imoveis ativos e realiza a busca dos imoveis
    message = f"Extraindo novos dados {business_type=}, {listing_type=}, {neighborhood=},  {locationId=},  {state=},  {city=},  {zone=}, {last_update=}, {force_update=}"
    with timeit(message, log, "info"):
        bd.clean_imoveis_ativos(db, listing_type, business_type, locationId)

        with ProcessPoolExecutor() as executor:
            futures = {
                executor.submit(
                    request_page.request_page,
                    origin=site,
                    neighborhood=neighborhood,
                    locationId=locationId,
                    state=state,
                    city=city,
                    zone=zone,
                    business_type=business_type,
                    listing_type=listing_type,
                ): site
                for site in settings["SITES"].keys()
            }

            for future in as_completed(futures):
                data = future.result()
                for parsed in Parallel()(
                    delayed(clean_data.clean_data)(d, df_metro) for d in data
                ):
                    url = parsed.url
                    imovel = Imovel.query.filter_by(url=url).first()

                    if imovel:
                        if (
                            force_update
                            or imovel.updated_date.date() != parsed.updated_date.date()
                        ):
                            with timeit(f"Update {url}", log, "info"):
                                imovel.raw = parsed.raw
                                imovel.title = parsed.title
                                imovel.usable_area = parsed.usable_area
                                imovel.floors = parsed.floors
                                imovel.type_unit = parsed.type_unit
                                imovel.bedrooms = parsed.bedrooms
                                imovel.bathrooms = parsed.bathrooms
                                imovel.suites = parsed.suites
                                imovel.parking_spaces = parsed.parking_spaces
                                imovel.amenities = parsed.amenities
                                imovel.images = parsed.images
                                imovel.address = parsed.address
                                imovel.address_lat = parsed.address_lat
                                imovel.address_lon = parsed.address_lon
                                imovel.price = parsed.price
                                imovel.condo_fee = parsed.condo_fee
                                imovel.total_fee = parsed.total_fee
                                imovel.linha = parsed.linha
                                imovel.estacao = parsed.estacao
                                imovel.lat_metro = parsed.lat_metro
                                imovel.lon_metro = parsed.lon_metro
                                imovel.distance = parsed.distance
                                imovel.updated_date = parsed.updated_date
                        else:
                            log.debug(f"not updated {url}")

                    else:
                        with timeit(f"creating {url}", log, "info"):
                            db.session.add(parsed)
                            db.session.commit()

                    if not ImovelAtivo.query.filter_by(url=url).first():
                        imovel_ativo = ImovelAtivo(
                            url=url,
                            location_id=locationId,
                            business_type=business_type,
                            listing_type=listing_type,
                        )
                        db.session.add(imovel_ativo)
                        db.session.commit()

        db.session.commit()
        update_predict.update_predict(db, locationId, business_type, listing_type)

        return get_activated_listings.get_activated_listings(
            db.engine, locationId, business_type, listing_type
        )
