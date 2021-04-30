import logging
import requests
import jsonlines
from math import ceil
from time import sleep
from datetime import datetime
from os.path import exists, join, getmtime
from concurrent.futures import ProcessPoolExecutor, as_completed

log = logging.getLogger(__name__)


def request(
    origin: str,
    conf: dict,
    neighborhood,
    locationId,
    state,
    city,
    zone,
    business_type: str = None,
    listing_type: str = None,
    size: int = 24,
):
    assert origin in ["zapimoveis", "vivareal"]
    assert business_type in ["RENTAL", "SALE"]
    assert listing_type in ["USED", "DEVELOPMENT"]

    pages = conf["max_page"]
    api = conf["site"][origin]["api"]
    site = conf["site"][origin]["site"]
    portal = conf["site"][origin]["portal"]

    headers = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
        "sec-ch-ua": 'Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
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
        "includeFields": "search(result(listings(listing(displayAddressType,amenities,usableAreas,constructionStatus,listingType,description,title,createdAt,floors,unitTypes,nonActivationReason,providerId,propertyType,unitSubTypes,unitsOnTheFloor,legacyId,id,portal,unitFloor,parkingSpaces,updatedAt,address,suites,publicationType,externalId,bathrooms,usageTypes,totalAreas,advertiserId,advertiserContact,whatsappNumber,bedrooms,acceptExchange,pricingInfos,showPrice,resale,buildings,capacityLimit,status),account(id,name,logoUrl,licenseNumber,showAddress,legacyVivarealId,legacyZapId,minisite),medias,accountLink,link)),totalCount),expansion(search(result(listings(listing(displayAddressType,amenities,usableAreas,constructionStatus,listingType,description,title,createdAt,floors,unitTypes,nonActivationReason,providerId,propertyType,unitSubTypes,unitsOnTheFloor,legacyId,id,portal,unitFloor,parkingSpaces,updatedAt,address,suites,publicationType,externalId,bathrooms,usageTypes,totalAreas,advertiserId,advertiserContact,whatsappNumber,bedrooms,acceptExchange,pricingInfos,showPrice,resale,buildings,capacityLimit,status),account(id,name,logoUrl,licenseNumber,showAddress,legacyVivarealId,legacyZapId,minisite),medias,accountLink,link)),totalCount)),nearby(search(result(listings(listing(displayAddressType,amenities,usableAreas,constructionStatus,listingType,description,title,createdAt,floors,unitTypes,nonActivationReason,providerId,propertyType,unitSubTypes,unitsOnTheFloor,legacyId,id,portal,unitFloor,parkingSpaces,updatedAt,address,suites,publicationType,externalId,bathrooms,usageTypes,totalAreas,advertiserId,advertiserContact,whatsappNumber,bedrooms,acceptExchange,pricingInfos,showPrice,resale,buildings,capacityLimit,status),account(id,name,logoUrl,licenseNumber,showAddress,legacyVivarealId,legacyZapId,minisite),medias,accountLink,link)),totalCount)),page,fullUriFragments,developments(search(result(listings(listing(displayAddressType,amenities,usableAreas,constructionStatus,listingType,description,title,createdAt,floors,unitTypes,nonActivationReason,providerId,propertyType,unitSubTypes,unitsOnTheFloor,legacyId,id,portal,unitFloor,parkingSpaces,updatedAt,address,suites,publicationType,externalId,bathrooms,usageTypes,totalAreas,advertiserId,advertiserContact,whatsappNumber,bedrooms,acceptExchange,pricingInfos,showPrice,resale,buildings,capacityLimit,status),account(id,name,logoUrl,licenseNumber,showAddress,legacyVivarealId,legacyZapId,minisite),medias,accountLink,link)),totalCount)),superPremium(search(result(listings(listing(displayAddressType,amenities,usableAreas,constructionStatus,listingType,description,title,createdAt,floors,unitTypes,nonActivationReason,providerId,propertyType,unitSubTypes,unitsOnTheFloor,legacyId,id,portal,unitFloor,parkingSpaces,updatedAt,address,suites,publicationType,externalId,bathrooms,usageTypes,totalAreas,advertiserId,advertiserContact,whatsappNumber,bedrooms,acceptExchange,pricingInfos,showPrice,resale,buildings,capacityLimit,status),account(id,name,logoUrl,licenseNumber,showAddress,legacyVivarealId,legacyZapId,minisite),medias,accountLink,link)),totalCount)),owners(search(result(listings(listing(displayAddressType,amenities,usableAreas,constructionStatus,listingType,description,title,createdAt,floors,unitTypes,nonActivationReason,providerId,propertyType,unitSubTypes,unitsOnTheFloor,legacyId,id,portal,unitFloor,parkingSpaces,updatedAt,address,suites,publicationType,externalId,bathrooms,usageTypes,totalAreas,advertiserId,advertiserContact,whatsappNumber,bedrooms,acceptExchange,pricingInfos,showPrice,resale,buildings,capacityLimit,status),account(id,name,logoUrl,licenseNumber,showAddress,legacyVivarealId,legacyZapId,minisite),medias,accountLink,link)),totalCount))",
        "addressNeighborhood": neighborhood,
        "addressLocationId": locationId,
        "addressState": state,
        "addressCity": city,
        "addressZone": zone,
        "listingType": listing_type,
        "business": business_type,
        "categoryPage": "RESULT",
        "usageTypes": "RESIDENTIAL",
        "size": size,
        "from": 24,
    }

    listings = requests.get(base_url, params=query, headers=headers).json()

    total_listings = listings["search"]["totalCount"]
    max_page = ceil(total_listings / query["size"])
    log.info(f"Total listings: {total_listings} and max pages: {max_page}")
    pages = min(pages, max_page)
    if pages == -1:
        pages = max_page
    log.info(f"Getting {pages} pages")

    data = []
    for page in range(pages):
        query["from"] = page * query["size"]

        try:
            r = requests.get(base_url, params=query, headers=headers)
            r.raise_for_status()
            log.info(f"Getting page {page+1}/{pages} from {portal} OK")
        except requests.exceptions.HTTPError as e:
            log.error(f"Getting page {page+1}/{pages} from {portal}: {e}")
            raise e

        data += r.json()["search"]["result"]["listings"]
        sleep(0.05)

    for d in data:
        d["url"] = site + d["link"]["href"]

    return data


def run_request(
    conf: dict, neighborhood, locationId, state, city, zone, business_type, listing_type
):
    log.info(
        " | ".join(
            [business_type, listing_type, neighborhood, locationId, state, city, zone]
        )
    )

    data: list = []
    filename = locationId.replace(" ", "_").replace(">", "_")
    filename = f"{business_type}_{listing_type}_{filename}"
    filename = join(conf["dir_input"], filename + ".jsonl")

    if exists(filename):
        modification_datetime = datetime.fromtimestamp(getmtime(filename))

        if datetime.now().date != modification_datetime.date():
            log.info(f"Reading '{filename}'")
            with jsonlines.open(filename) as reader:
                return [obj for obj in reader], filename, False

    with ProcessPoolExecutor() as executor:
        for site in conf["site"].keys():
            futures = {
                executor.submit(
                    request,
                    site,
                    conf,
                    neighborhood,
                    locationId,
                    state,
                    city,
                    zone,
                    business_type,
                    listing_type,
                ): site
            }

        for future in as_completed(futures):
            site = futures[future]
            try:
                data += future.result()
            except Exception as e:
                log.error(f"{site}: {e}")

    if data:
        log.info(f"Writing file '{filename}'")
        with jsonlines.open(filename, mode="w") as writer:
            writer.write_all(data)

    return data, filename, True
