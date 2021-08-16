import requests
import pandas as pd
from math import ceil
from time import sleep
from datetime import datetime
from flask import current_app
from concurrent.futures import ProcessPoolExecutor, as_completed


from listings.models import Imovel, ImovelAtivo
from listings.backend.preprocess import preprocess
from listings.extensions.serializer import ImovelSchema

IS = ImovelSchema(many=True)


def _request(
    origin: str,
    neighborhood,
    locationId,
    state,
    city,
    zone,
    df_metro: pd.DataFrame,
    business_type: str = None,
    listing_type: str = None,
    size: int = 24,
) -> list:
    """
    Request all pages for one site
    """
    conf = current_app.config

    pages = conf["max_page"]
    api = conf["sites"][origin]["api"]
    site = conf["sites"][origin]["site"]
    portal = conf["sites"][origin]["portal"]

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
        "sort": "updatedAt DESC",
        "size": size,
        "from": 24,
    }

    listings = requests.get(base_url, params=query, headers=headers).json()

    if "search" in listings.keys():
        total_listings = listings["search"]["totalCount"]
        max_page = ceil(total_listings / query["size"])
        current_app.logger.info(
            f"{portal} total listings: {total_listings} and max pages: {max_page}"
        )
        pages = min(pages, max_page)
        if pages == -1:
            pages = max_page
        current_app.logger.info(f"{portal} getting {pages} pages")

        data = []
        for page in range(pages):
            query["from"] = page * query["size"]

            try:
                r = requests.get(base_url, params=query, headers=headers)
                r.raise_for_status()
                current_app.logger.info(
                    f"Getting page {page+1}/{pages} from {portal} OK"
                )
                data += r.json()["search"]["result"]["listings"]
                sleep(0.05)

            except requests.exceptions.HTTPError as e:
                current_app.logger.error(
                    f"Getting page {page+1}/{pages} from {portal}: {e}"
                )

        new_data = []
        for d in data:
            d["url"] = site + d["link"]["href"]
            processed_data = preprocess(d, business_type, df_metro)
            new_data.append((d, processed_data))

        return new_data

    raise Exception(listings)


def get_activated_listings(locationId, business_type, listing_type):
    imoveis = current_app.db.engine.execute(
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


def get_listings(
    neighborhood,
    locationId,
    state,
    city,
    zone,
    business_type,
    listing_type,
    df_metro: pd.DataFrame,
) -> pd.DataFrame:

    # Para dados que já foram atualizados no dia da consulta, apenas retorna os dados
    last_update = current_app.db.engine.execute(
        f"""
        SELECT max(updated_date)
        FROM imovel_ativo
        WHERE
            listing_type = '{listing_type}'
            and business_type = '{business_type}'
            and location_id = '{locationId}'
        """
    ).scalar()

    current_app.logger.info(
        f"{business_type=}, {listing_type=}, {neighborhood=},  {locationId=},  {state=},  {city=},  {zone=}, {last_update=}"
    )

    # Caso ja tenha dados atualizados do dia corrente
    if last_update and last_update.date() == datetime.today().date():
        return get_activated_listings(locationId, business_type, listing_type)

    # Caso contrário, limpa dados dos imoveis ativos e realiza a busca dos imoveis
    ImovelAtivo.query.delete()

    with ProcessPoolExecutor() as executor:
        futures = {
            executor.submit(
                _request,
                origin=site,
                neighborhood=neighborhood,
                locationId=locationId,
                state=state,
                city=city,
                zone=zone,
                business_type=business_type,
                listing_type=listing_type,
                df_metro=df_metro,
            ): site
            for site in current_app.config["sites"].keys()
        }

    for future in as_completed(futures):
        for d, p in future.result():
            imovel = Imovel.query.filter_by(url=d["url"]).first()

            if imovel:
                if imovel.updated_date != p["updatedAt"]:
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
                    imovel.address_lat = p["address_lat"]
                    imovel.address_lon = p["address_lon"]
                    imovel.price = p["price"]
                    imovel.condo_fee = p["condo_fee"]
                    imovel.total_fee = p["total_fee"]
                    imovel.linha = p["linha"]
                    imovel.estacao = p["estacao"]
                    imovel.distance = p["distance"]
                    imovel.updated_date = p["updatedAt"]

            else:
                imovel = Imovel(
                    url=d["url"],
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
                current_app.db.session.add(imovel)

            imovel_ativo = ImovelAtivo.query.filter_by(url=d["url"]).first()
            if not imovel_ativo:
                imovel_ativo = ImovelAtivo(
                    url=d["url"],
                    location_id=locationId,
                    business_type=business_type,
                    listing_type=listing_type,
                )
                current_app.db.session.add(imovel_ativo)

    current_app.db.session.commit()

    return get_activated_listings(locationId, business_type, listing_type)
