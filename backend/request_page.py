import logging
import requests
from math import ceil
from time import sleep


log = logging.getLogger(__name__)


def request_page(
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
        "referer": f"https://www.{origin}.com.br",
        "origin": f"https://www.{origin}.com.br",
        "x-domain": f"www.{origin}.com.br",
    }

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
                sleep(0.15)

            except requests.exceptions.HTTPError as e:
                log.error(f"Getting page {page+1}/{max_page} from {portal}: {e}")

        log.info(f"Busca dos dados do {portal} foi finalizada")

        return site, data

    raise Exception(listings)
