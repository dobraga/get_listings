import logging
import requests
import jsonlines
from math import ceil
from time import sleep
from copy import deepcopy
from datetime import datetime, timedelta
from os.path import exists, join, getmtime

# from concurrent.futures import ProcessPoolExecutor, as_completed

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

confs = {
    "vivareal": {"site": "glue-api.vivareal.com", "portal": "VIVAREAL"},
    "zapimoveis": {"site": "glue-api.zapimoveis.com.br", "portal": "ZAP"},
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
        self.site = confs[origin]["site"]
        self.portal = confs[origin]["portal"]

        self.headers = headers
        self.headers["referer"] = f"https://www.{self.origin}.com.br"
        self.headers["origin"] = f"https://www.{self.origin}.com.br"
        self.headers["x-domain"] = f"www.{self.origin}.com.br"

        self.position = conf.get("postition_loc", None)
        self.pages = pages
        self.size = size

        self.set_location()

    def set_location(self) -> None:
        base_url = f"https://{self.site}/v3/locations"

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

    def get_listings(self) -> list:

        self.new_file = True

        if exists(self.filename):
            modification_datetime = datetime.fromtimestamp(getmtime(self.filename))
            threshold_time = datetime.now() - timedelta(minutes=30)

            if threshold_time < modification_datetime:
                log.info(f"Reading '{self.filename}'")
                self.new_file = False
                with jsonlines.open(self.filename) as reader:
                    return [obj for obj in reader]
            else:
                log.info(
                    f"Not reading '{self.filename}' because modification is in {str(modification_datetime)}"
                )

        base_url = f"https://{self.site}/v2/listings"

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
        if pages == -1:
            total_listings = listings["search"]["totalCount"]
            pages = ceil(total_listings / query["size"])

        data = []
        for page in range(pages):
            query_ = deepcopy(query)
            query_["from"] = page * query_["size"]

            try:
                r = requests.get(base_url, params=query_, headers=headers)
                r.raise_for_status()
            except requests.exceptions.HTTPError as e:
                log.error(e)
                raise e

            data += r.json()["search"]["result"]["listings"]
            sleep(0.01)

        return data


def run_request(conf: dict, local: str = None):
    data: list = []
    for site in conf["site"]:
        req = Request(site, conf, query_location=local)
        data += req.get_listings()

    log.info(f"Writing file '{req.filename}'")
    with jsonlines.open(req.filename, mode="w") as writer:
        writer.write_all(data)

    return data, req.local, req.filename, req.new_file
