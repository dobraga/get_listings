import logging
import requests
from math import ceil
from time import sleep
from typing import Union

from backend.timeit import timeit
from backend.settings import settings


log = logging.getLogger(__name__)


def request_page(
    origin: str,
    neighborhood: str,
    locationId: str,
    state: str,
    city: str,
    zone: str,
    business_type: str,
    listing_type: str,
    size: int = 24,
    max_page: int = None,
    **kwargs,
) -> list:
    """
    Request all pages for one site
    """

    with timeit(f"Busca dados do {origin}", log):
        max_page = max_page or settings["max_page"]
        api = settings["sites"][origin]["api"]
        site = settings["sites"][origin]["site"]
        portal = settings["sites"][origin]["portal"]

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

        query: dict[str, Union[int, str]] = {
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

        default_values = {
            "neighborhood": neighborhood,
            "locationId": locationId,
            "state": state,
            "city": city,
            "zone": zone,
            "business_type": business_type,
            "listing_type": listing_type,
            "origin": origin,
        }

        listings = requests.get(base_url, params=query, headers=headers).json()

        if "search" in listings.keys():
            total_listings = listings["search"]["totalCount"]
            total_pages = ceil(total_listings / query["size"])
            log.info(
                f"{portal} total listings: {total_listings} and max pages: {total_pages}"
            )
            max_page = min(max_page, total_pages)
            if max_page == -1:
                max_page = total_pages
            log.info(f"{portal} getting {max_page} pages")

            data = []
            for page in range(1, max_page + 1):
                with timeit(
                    f"Getting page {page}/{max_page} from {portal} OK", log, "debug"
                ):
                    try:
                        query["from"] = page * query["size"]
                        r = requests.get(base_url, params=query, headers=headers)
                        r.raise_for_status()
                        data += r.json()["search"]["result"]["listings"]
                        sleep(settings["sites"][origin]["sleep"])

                    except requests.exceptions.HTTPError as e:
                        log.error(f"Getting page {page}/{max_page} from {portal}: {e}")
                        break

            data = [
                dict(d, **default_values, **{"url": site + d["link"]["href"]})
                for d in data
            ]

            return data

        raise Exception(listings)
