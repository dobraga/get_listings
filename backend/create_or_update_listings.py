import logging
from joblib import Parallel, delayed
from concurrent.futures import ProcessPoolExecutor, as_completed

from backend.timeit import timeit
from backend.metro import get_metro
from backend.settings import settings
from dashboard.models import Imovel, ImovelAtivo
from backend import clean_data, request_page, update_predict, bd

log = logging.getLogger(__name__)


def create_or_update_listings(
    locationId: str,
    neighborhood: str,
    state: str,
    stateAcronym: str,
    city: str,
    zone: str,
    business_type: str,
    listing_type: str,
    db,
):
    message = f"Extraindo novos dados {business_type=}, {listing_type=}, {locationId=}"

    force_update = settings.get("FORCE_UPDATE", False)
    df_metro = get_metro(stateAcronym.lower(), db)

    with timeit(message, log):
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
                for site in settings["sites"].keys()
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
                            or imovel.updated_date is None
                            or parsed.updated_date is None
                            or imovel.updated_date.date() != parsed.updated_date.date()
                        ):
                            with timeit(f"Update {url}", log, "debug"):
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
                        with timeit(f"creating {url}", log, "debug"):
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
