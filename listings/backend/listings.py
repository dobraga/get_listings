import logging
import requests
import pandas as pd
from math import ceil
from time import sleep
from datetime import datetime
from joblib import Parallel, delayed
from concurrent.futures import ProcessPoolExecutor, as_completed

from listings.backend.model import predict
from listings.models import Imovel, ImovelAtivo
from listings.backend.preprocess import preprocess
from listings.extensions.serializer import ImovelSchema

log = logging.getLogger(__name__)
IS = ImovelSchema(many=True)


def _request(
    max_page,
    api,
    site,
    portal,
    origin: str,
    neighborhood,
    locationId,
    state,
    city,
    zone,
    business_type: str = None,
    listing_type: str = None,
    size: int = 24,
) -> tuple:
    """
    Request all pages for one site
    """

    log.info(f"Buscando dados do {portal}")

    headers = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
        "accept-language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "sec-fetch-site": "same-site",
        "accept": "application/json",
        "sec-fetch-dest": "empty",
        "sec-ch-ua-mobile": "?0",
        "sec-fetch-mode": "cors",
        "origin-ua-mobile": "?0",
    }

    headers["referer"] = f"https://www.{origin}.com.br"
    headers["origin"] = f"https://www.{origin}.com.br"
    headers["x-domain"] = f"www.{origin}.com.br"

    base_url = f"https://{api}/v2/listings"

    query = {
        "includeFields": "search(result(listings(listing(displayAddressType,amenities,usableAreas,constructionStatus,listingType,description,title,stamps,createdAt,floors,unitTypes,nonActivationReason,providerId,propertyType,unitSubTypes,unitsOnTheFloor,legacyId,id,portal,unitFloor,parkingSpaces,updatedAt,address,suites,publicationType,externalId,bathrooms,usageTypes,totalAreas,advertiserId,advertiserContact,whatsappNumber,bedrooms,acceptExchange,pricingInfos,showPrice,resale,buildings,capacityLimit,status),account(id,name,logoUrl,licenseNumber,showAddress,legacyVivarealId,legacyZapId,minisite),medias,accountLink,link)),totalCount),expansion(search(result(listings(listing(displayAddressType,amenities,usableAreas,constructionStatus,listingType,description,title,stamps,createdAt,floors,unitTypes,nonActivationReason,providerId,propertyType,unitSubTypes,unitsOnTheFloor,legacyId,id,portal,unitFloor,parkingSpaces,updatedAt,address,suites,publicationType,externalId,bathrooms,usageTypes,totalAreas,advertiserId,advertiserContact,whatsappNumber,bedrooms,acceptExchange,pricingInfos,showPrice,resale,buildings,capacityLimit,status),account(id,name,logoUrl,licenseNumber,showAddress,legacyVivarealId,legacyZapId,minisite),medias,accountLink,link)),totalCount)),nearby(search(result(listings(listing(displayAddressType,amenities,usableAreas,constructionStatus,listingType,description,title,stamps,createdAt,floors,unitTypes,nonActivationReason,providerId,propertyType,unitSubTypes,unitsOnTheFloor,legacyId,id,portal,unitFloor,parkingSpaces,updatedAt,address,suites,publicationType,externalId,bathrooms,usageTypes,totalAreas,advertiserId,advertiserContact,whatsappNumber,bedrooms,acceptExchange,pricingInfos,showPrice,resale,buildings,capacityLimit,status),account(id,name,logoUrl,licenseNumber,showAddress,legacyVivarealId,legacyZapId,minisite),medias,accountLink,link)),totalCount)),page,fullUriFragments,developments(search(result(listings(listing(displayAddressType,amenities,usableAreas,constructionStatus,listingType,description,title,stamps,createdAt,floors,unitTypes,nonActivationReason,providerId,propertyType,unitSubTypes,unitsOnTheFloor,legacyId,id,portal,unitFloor,parkingSpaces,updatedAt,address,suites,publicationType,externalId,bathrooms,usageTypes,totalAreas,advertiserId,advertiserContact,whatsappNumber,bedrooms,acceptExchange,pricingInfos,showPrice,resale,buildings,capacityLimit,status),account(id,name,logoUrl,licenseNumber,showAddress,legacyVivarealId,legacyZapId,minisite),medias,accountLink,link)),totalCount)),superPremium(search(result(listings(listing(displayAddressType,amenities,usableAreas,constructionStatus,listingType,description,title,stamps,createdAt,floors,unitTypes,nonActivationReason,providerId,propertyType,unitSubTypes,unitsOnTheFloor,legacyId,id,portal,unitFloor,parkingSpaces,updatedAt,address,suites,publicationType,externalId,bathrooms,usageTypes,totalAreas,advertiserId,advertiserContact,whatsappNumber,bedrooms,acceptExchange,pricingInfos,showPrice,resale,buildings,capacityLimit,status),account(id,name,logoUrl,licenseNumber,showAddress,legacyVivarealId,legacyZapId,minisite),medias,accountLink,link)),totalCount)),owners(search(result(listings(listing(displayAddressType,amenities,usableAreas,constructionStatus,listingType,description,title,stamps,createdAt,floors,unitTypes,nonActivationReason,providerId,propertyType,unitSubTypes,unitsOnTheFloor,legacyId,id,portal,unitFloor,parkingSpaces,updatedAt,address,suites,publicationType,externalId,bathrooms,usageTypes,totalAreas,advertiserId,advertiserContact,whatsappNumber,bedrooms,acceptExchange,pricingInfos,showPrice,resale,buildings,capacityLimit,status),account(id,name,logoUrl,licenseNumber,showAddress,legacyVivarealId,legacyZapId,minisite),medias,accountLink,link)),totalCount))",
        "addressNeighborhood": neighborhood,
        "addressLocationId": locationId,
        "addressState": state,
        "addressCity": city,
        "addressZone": zone,
        "listingType": listing_type,
        "business": business_type,
        "usageTypes": "RESIDENTIAL",
        "categoryPage": "RESULT",
        "size": size,
        "from": 24,
    }

    listings = requests.get(base_url, params=query, headers=headers).json()

    if "search" in listings.keys():
        total_listings = listings["search"]["totalCount"]
        max_page_ = ceil(total_listings / query["size"])
        log.info(
            f"{portal} total listings: {total_listings} and max pages: {max_page_}"
        )
        max_page = min(max_page, max_page_)
        if max_page == -1:
            max_page = max_page_
        log.info(f"{portal} getting {max_page} pages")

        data = []
        for page in range(max_page):
            try:
                query["from"] = page * query["size"]
                r = requests.get(base_url, params=query, headers=headers)
                r.raise_for_status()
                log.info(f"Getting page {page+1}/{max_page} from {portal} OK")
                data += r.json()["search"]["result"]["listings"]
                sleep(0.05)

            except requests.exceptions.HTTPError as e:
                log.error(f"Getting page {page+1}/{max_page} from {portal}: {e}")

        log.info(f"Busca dos dados do {portal} foi finalizada")

        return site, data

    raise Exception(listings)


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


def update_predict(engine, locationId, business_type, listing_type) -> None:
    log.info("Atualizando previsão de preços")

    imoveis = engine.execute(
        f"""
        SELECT *
        FROM imovel
        WHERE
            listing_type = '{listing_type}'
            and business_type = '{business_type}'
            and location_id = '{locationId}'
    """
    ).all()

    if imoveis:
        df = pd.DataFrame(IS.dump(imoveis))
        df["pred"] = predict(df)

        for _, (url, pred) in df[["url", "pred"]].iterrows():
            log.debug(f"Atualizando a previsão de '{url}' para {pred}")
            Imovel.query.filter_by(url=url).first().total_fee_predict = pred
    else:
        log.info("Nenhum imóvel encontrado")

    log.info("Atualização da previsão de preços finalizada")


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
    config,
    **kwargs,
) -> pd.DataFrame:

    force_update = config.get("FORCE_UPDATE", False)

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
        return preprocess(x, business_type=business_type, df_metro=df_metro)

    with ProcessPoolExecutor() as executor:
        futures = {
            executor.submit(
                _request,
                max_page=config["MAX_PAGE"],
                api=config["SITES"][site]["api"],
                site=config["SITES"][site]["site"],
                portal=config["SITES"][site]["portal"],
                origin=site,
                neighborhood=neighborhood,
                locationId=locationId,
                state=state,
                city=city,
                zone=zone,
                business_type=business_type,
                listing_type=listing_type,
            ): site
            for site in config["SITES"].keys()
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
                        distance=p["distance"],
                        created_date=p["createdAt"],
                        updated_date=p["updatedAt"],
                    )
                    db.session.add(imovel)
                    log.debug(f"created {url}")

                if not ImovelAtivo.query.filter_by(url=url).first():
                    imovel_ativo = ImovelAtivo(
                        url=url,
                        location_id=locationId,
                        business_type=business_type,
                        listing_type=listing_type,
                    )
                    db.session.add(imovel_ativo)

    update_predict(db.engine, locationId, business_type, listing_type)

    db.session.commit()

    df = get_activated_listings(db.engine, locationId, business_type, listing_type)

    return df
