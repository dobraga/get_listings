import logging
import requests
import jsonlines
from math import ceil
from time import sleep
from copy import deepcopy
from datetime import datetime
from os.path import exists, join, getmtime
from concurrent.futures import ProcessPoolExecutor, as_completed

log = logging.getLogger(__name__)

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


class Request:
    def __init__(
        self,
        origin: str,
        conf: dict,
        size: int = 24,
        query_location: str = None,
        business_type: str = None,
        listing_type: str = None,
    ) -> None:
        self.query_location = query_location or conf["local"]
        self.business_type = business_type or conf["tipo_contrato"]
        self.listing_type = listing_type or conf["tipo_propriedade"]
        self.path = conf["dir_input"]
        pages = conf["max_page"]

        assert origin in ["zapimoveis", "vivareal"]
        assert self.business_type in ["RENTAL", "SALE"]
        assert self.listing_type in ["USED", "DEVELOPMENT"]

        self.origin = origin
        self.api = conf["site"][origin]["api"]
        self.site = conf["site"][origin]["site"]
        self.portal = conf["site"][origin]["portal"]

        self.headers = headers
        self.headers["referer"] = f"https://www.{self.origin}.com.br"
        self.headers["origin"] = f"https://www.{self.origin}.com.br"
        self.headers["x-domain"] = f"www.{self.origin}.com.br"

        self.position = conf.get("postition_loc", None)
        self.pages = pages
        self.size = size

        self.set_location()

    def set_location(self) -> None:
        base_url = f"https://{self.api}/v3/locations"

        query = {
            "businessType": self.business_type,
            "listingType": self.listing_type,
            "q": self.query_location,
            "fields": "neighborhood",
            "portal": self.portal,
            "size": "6",
        }

        try:
            r = requests.get(base_url, params=query, headers=self.headers)
            r.raise_for_status()
            sleep(0.5)
        except requests.exceptions.HTTPError as e:
            log.error(e)
            raise e

        locations = r.json()["neighborhood"]["result"]["locations"]

        position = self.position
        if position is None:
            print("Select location: ")
            position = int(input())

        log.info(
            f"{self.portal}\n\n"
            + "\n".join(
                [
                    f"{i}: {local['address']['locationId']} {'<-' if i == position else ''}"
                    for i, local in enumerate(locations)
                ]
            )
        )

        self.local = locations[position]["address"]

        self.filename = self.local["locationId"].replace(" ", "_").replace(">", "_")
        self.filename = join(self.path, self.filename + ".jsonl")

    def get_listings(self) -> tuple:

        new_file = True

        if exists(self.filename):
            modification_datetime = datetime.fromtimestamp(getmtime(self.filename))

            if datetime.now().date != modification_datetime.date():
                log.info(f"Reading '{self.filename}'")
                new_file = False
                with jsonlines.open(self.filename) as reader:
                    return [obj for obj in reader], new_file
            else:
                log.info(
                    f"Not reading '{self.filename}' because modification is in {str(modification_datetime)}"
                )

        base_url = f"https://{self.api}/v2/listings"

        query = {
            "includeFields": "search(result(listings(listing(displayAddressType,amenities,usableAreas,constructionStatus,listingType,description,title,createdAt,floors,unitTypes,nonActivationReason,providerId,propertyType,unitSubTypes,unitsOnTheFloor,legacyId,id,portal,unitFloor,parkingSpaces,updatedAt,address,suites,publicationType,externalId,bathrooms,usageTypes,totalAreas,advertiserId,advertiserContact,whatsappNumber,bedrooms,acceptExchange,pricingInfos,showPrice,resale,buildings,capacityLimit,status),account(id,name,logoUrl,licenseNumber,showAddress,legacyVivarealId,legacyZapId,minisite),medias,accountLink,link)),totalCount),expansion(search(result(listings(listing(displayAddressType,amenities,usableAreas,constructionStatus,listingType,description,title,createdAt,floors,unitTypes,nonActivationReason,providerId,propertyType,unitSubTypes,unitsOnTheFloor,legacyId,id,portal,unitFloor,parkingSpaces,updatedAt,address,suites,publicationType,externalId,bathrooms,usageTypes,totalAreas,advertiserId,advertiserContact,whatsappNumber,bedrooms,acceptExchange,pricingInfos,showPrice,resale,buildings,capacityLimit,status),account(id,name,logoUrl,licenseNumber,showAddress,legacyVivarealId,legacyZapId,minisite),medias,accountLink,link)),totalCount)),nearby(search(result(listings(listing(displayAddressType,amenities,usableAreas,constructionStatus,listingType,description,title,createdAt,floors,unitTypes,nonActivationReason,providerId,propertyType,unitSubTypes,unitsOnTheFloor,legacyId,id,portal,unitFloor,parkingSpaces,updatedAt,address,suites,publicationType,externalId,bathrooms,usageTypes,totalAreas,advertiserId,advertiserContact,whatsappNumber,bedrooms,acceptExchange,pricingInfos,showPrice,resale,buildings,capacityLimit,status),account(id,name,logoUrl,licenseNumber,showAddress,legacyVivarealId,legacyZapId,minisite),medias,accountLink,link)),totalCount)),page,fullUriFragments,developments(search(result(listings(listing(displayAddressType,amenities,usableAreas,constructionStatus,listingType,description,title,createdAt,floors,unitTypes,nonActivationReason,providerId,propertyType,unitSubTypes,unitsOnTheFloor,legacyId,id,portal,unitFloor,parkingSpaces,updatedAt,address,suites,publicationType,externalId,bathrooms,usageTypes,totalAreas,advertiserId,advertiserContact,whatsappNumber,bedrooms,acceptExchange,pricingInfos,showPrice,resale,buildings,capacityLimit,status),account(id,name,logoUrl,licenseNumber,showAddress,legacyVivarealId,legacyZapId,minisite),medias,accountLink,link)),totalCount)),superPremium(search(result(listings(listing(displayAddressType,amenities,usableAreas,constructionStatus,listingType,description,title,createdAt,floors,unitTypes,nonActivationReason,providerId,propertyType,unitSubTypes,unitsOnTheFloor,legacyId,id,portal,unitFloor,parkingSpaces,updatedAt,address,suites,publicationType,externalId,bathrooms,usageTypes,totalAreas,advertiserId,advertiserContact,whatsappNumber,bedrooms,acceptExchange,pricingInfos,showPrice,resale,buildings,capacityLimit,status),account(id,name,logoUrl,licenseNumber,showAddress,legacyVivarealId,legacyZapId,minisite),medias,accountLink,link)),totalCount)),owners(search(result(listings(listing(displayAddressType,amenities,usableAreas,constructionStatus,listingType,description,title,createdAt,floors,unitTypes,nonActivationReason,providerId,propertyType,unitSubTypes,unitsOnTheFloor,legacyId,id,portal,unitFloor,parkingSpaces,updatedAt,address,suites,publicationType,externalId,bathrooms,usageTypes,totalAreas,advertiserId,advertiserContact,whatsappNumber,bedrooms,acceptExchange,pricingInfos,showPrice,resale,buildings,capacityLimit,status),account(id,name,logoUrl,licenseNumber,showAddress,legacyVivarealId,legacyZapId,minisite),medias,accountLink,link)),totalCount))",
            "addressNeighborhood": self.local["neighborhood"],
            "addressLocationId": self.local["locationId"],
            "addressState": self.local["state"],
            "addressCity": self.local["city"],
            "addressZone": self.local["zone"],
            "listingType": self.listing_type,
            "business": self.business_type,
            "categoryPage": "RESULT",
            "usageTypes": "RESIDENTIAL",
            "size": 24,
            "from": 24,
        }

        listings = requests.get(base_url, params=query, headers=headers).json()

        pages = self.pages
        total_listings = listings["search"]["totalCount"]
        max_page = ceil(total_listings / query["size"])
        log.info(f"Max pages: {max_page}")
        pages = min(pages, max_page)
        if pages == -1:
            pages = max_page
        log.info(f"Getting {pages} pages")

        data = []
        for page in range(pages):
            query_ = deepcopy(query)
            query_["from"] = page * query_["size"]

            try:
                r = requests.get(base_url, params=query_, headers=headers)
                r.raise_for_status()
                log.info(f"Getting page {page+1}/{pages} from {self.portal} OK")
            except requests.exceptions.HTTPError as e:
                log.error(f"Getting page {page+1}/{pages} from {self.portal}: {e}")
                raise e

            data += r.json()["search"]["result"]["listings"]
            sleep(0.05)

        for d in data:
            d["url"] = self.site + d["link"]["href"]

        return data, new_file


def run_request(conf: dict, local: str = None):
    futures: dict = {}
    data: list = []
    new_file: bool = False

    with ProcessPoolExecutor() as executor:
        for site in conf["site"].keys():
            req = Request(site, conf, query_location=local)
            futures[executor.submit(req.get_listings)] = req

        for future in as_completed(futures):
            try:
                d, n = future.result()
                new_file = max(new_file, n)
                data += d
            except Exception as e:
                log.error(f"{req.portal}: {e}")

    log.info(f"Writing file '{req.filename}'")
    with jsonlines.open(req.filename, mode="w") as writer:
        writer.write_all(data)

    return data, req.local, req.filename, new_file
