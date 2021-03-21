import logging
import requests
import jsonlines
from math import ceil
from os import remove
from time import sleep
from os.path import join, exists

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
        out_file: str = "listings.jsonlines",
    ) -> None:
        query_location = conf["local"]
        business_type = conf["tipo_contrato"]
        listing_type = conf["tipo_propriedade"]
        pages = conf["max_page"]

        assert origin in ["zapimoveis", "vivareal"]
        assert business_type in ["RENTAL", "SALE"]
        assert listing_type in ["USED", "DEVELOPMENT"]

        self.origin = origin
        self.site = confs[origin]["site"]
        self.portal = confs[origin]["portal"]

        self.headers = headers
        self.headers["referer"] = f"https://www.{self.origin}.com.br"
        self.headers["origin"] = f"https://www.{self.origin}.com.br"
        self.headers["x-domain"] = f"www.{self.origin}.com.br"

        self.out_file = join(conf["dir_input"], out_file)
        self.position = conf.get("postition_loc", None)
        self.query_location = query_location
        self.business_type = business_type
        self.listing_type = listing_type
        self.pages = pages
        self.size = size

        if exists(self.out_file):
            remove(self.out_file)

        self.set_location()
        self.get_listings()

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

        locations = requests.get(base_url, params=query, headers=headers).json()
        locations = locations["neighborhood"]["result"]["locations"]

        print(
            f"{self.portal}\n\n",
            "\n".join(
                [
                    f"{i}: {local['address']['locationId']} "
                    for i, local in enumerate(locations)
                ]
            ),
            "\n\nSelect location: ",
            end="",
        )

        position = self.position if self.position is not None else int(input())

        self.local = locations[position]["address"]

    def get_listings(self) -> None:
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
        total_listings = listings["search"]["totalCount"]
        max_page = ceil(total_listings / query["size"])
        self.pages = max_page if self.pages == -1 else self.pages

        for page in range(self.pages):
            query["from"] = page * query["size"]

            listings = requests.get(base_url, params=query, headers=headers).json()
            listings = listings["search"]["result"]["listings"]

            with jsonlines.open(self.out_file, mode="a") as file:
                file.write_all(listings)

            log.info(f"Busca da página {page}/{max_page} do site {base_url} ok")

            sleep(0.1)


def run_request(conf: dict):
    for site in conf["site"]:
        Request(site, conf)
