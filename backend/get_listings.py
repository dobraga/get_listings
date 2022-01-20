import logging
import pandas as pd
from datetime import datetime
from joblib import Parallel, delayed
from concurrent.futures import ProcessPoolExecutor, as_completed


from backend.clean_data import clean_data
from backend.request_page import request_page
from backend.update_predict import update_predict
from backend.get_activated_listings import get_activated_listings

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
    last_update = db.engine.execute(
        f"""
        SELECT max(updated_date)
        FROM imovel_ativo
        WHERE
            listing_type = '{listing_type}'
            and business_type = '{business_type}'
            and location_id = '{locationId}'
        """
    ).scalar()

    # Caso ja tenha dados atualizados do dia corrente
    if (
        not force_update
        and last_update
        and last_update.date() == datetime.today().date()
    ):
        log.info(
            f"Reusando dados extraídos -> {business_type=}, {listing_type=}, {neighborhood=},  {locationId=},  {state=},  {city=},  {zone=}, {last_update=}"
        )
        return get_activated_listings(
            db.engine, locationId, business_type, listing_type
        )

    log.info(
        f"Extraindo novos dados -> {business_type=}, {listing_type=}, {neighborhood=},  {locationId=},  {state=},  {city=},  {zone=}, {last_update=}, {force_update=}"
    )

    # Caso contrário, limpa dados dos imoveis ativos e realiza a busca dos imoveis
    log.info(f"Limpando dados dos imóveis ativos")
    db.engine.execute(
        f"""
        DELETE FROM imovel_ativo
        WHERE
            listing_type = '{listing_type}'
            and business_type = '{business_type}'
            and location_id = '{locationId}'
        """
    )
    log.info(f"Limpeza concluida")

    def prep(x):
        return clean_data(x, business_type=business_type, df_metro=df_metro)

    with ProcessPoolExecutor() as executor:
        futures = {
            executor.submit(
                request_page,
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
            site, data = future.result()
            for d, p in Parallel()(delayed(prep)(d) for d in data):
                url = site + d["link"]["href"]
                imovel = Imovel.query.filter_by(url=url).first()

                if imovel:
                    if (
                        force_update
                        or imovel.updated_date.date() != p["updatedAt"].date()
                    ):
                        log.debug(
                            f"updating {url} because {imovel.updated_date.date()} != {p['updatedAt'].date()} or forced"
                        )

                        imovel.raw = d
                        imovel.title = p["title"]
                        imovel.usable_area = p["usable_area"]
                        imovel.floors = p["floors"]
                        imovel.type_unit = p["type_unit"]
                        imovel.bedrooms = p["bedrooms"]
                        imovel.bathrooms = p["bathrooms"]
                        imovel.suites = p["suites"]
                        imovel.parking_spaces = p["parking_spaces"]
                        imovel.amenities = p["amenities"]
                        imovel.images = p["images"]
                        imovel.address = p["address"]
                        imovel.address_lat = p["address_lat"]
                        imovel.address_lon = p["address_lon"]
                        imovel.price = p["price"]
                        imovel.condo_fee = p["condo_fee"]
                        imovel.total_fee = p["total_fee"]
                        imovel.linha = p["linha"]
                        imovel.estacao = p["estacao"]
                        imovel.lat_metro = p["lat_metro"]
                        imovel.lon_metro = p["lon_metro"]
                        imovel.distance = p["distance"]
                        imovel.updated_date = p["updatedAt"]

                        log.debug(f"updated {url}")
                    else:
                        log.debug(f"not updated {url}")

                else:
                    imovel = Imovel(
                        url=url,
                        neighborhood=neighborhood,
                        location_id=locationId,
                        state=state,
                        city=city,
                        zone=zone,
                        business_type=business_type,
                        listing_type=listing_type,
                        raw=d,
                        title=p["title"],
                        usable_area=p["usable_area"],
                        floors=p["floors"],
                        type_unit=p["type_unit"],
                        bedrooms=p["bedrooms"],
                        bathrooms=p["bathrooms"],
                        suites=p["suites"],
                        parking_spaces=p["parking_spaces"],
                        amenities=p["amenities"],
                        images=p["images"],
                        address=p["address"],
                        address_lat=p["address_lat"],
                        address_lon=p["address_lon"],
                        price=p["price"],
                        condo_fee=p["condo_fee"],
                        total_fee=p["total_fee"],
                        linha=p["linha"],
                        estacao=p["estacao"],
                        lat_metro=p["lat_metro"],
                        lon_metro=p["lon_metro"],
                        distance=p["distance"],
                        created_date=p["createdAt"],
                        updated_date=p["updatedAt"],
                    )
                    db.session.add(imovel)
                    db.session.commit()
                    log.debug(f"created {url}")

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
    update_predict(db, locationId, business_type, listing_type)

    return get_activated_listings(db.engine, locationId, business_type, listing_type)
