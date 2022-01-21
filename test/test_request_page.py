from backend import request_page, clean_data


def test_get_listings():

    selected_location = {
        "city": "Rio de Janeiro",
        "stateAcronym": "RJ",
        "zone": "Zona Norte",
        "locationId": "BR>Rio de Janeiro>NULL>Rio de Janeiro>Zona Norte>Tijuca",
        "state": "Rio de Janeiro",
        "neighborhood": "Tijuca",
    }

    imoveis_vivareal = request_page.request_page(
        max_page=1,
        origin="vivareal",
        business_type="RENTAL",
        listing_type="USED",
        **selected_location
    )

    assert len(imoveis_vivareal) > 10

    assert list(imoveis_vivareal[0].keys()) == [
        "listing",
        "account",
        "medias",
        "accountLink",
        "link",
        "neighborhood",
        "locationId",
        "state",
        "city",
        "zone",
        "business_type",
        "listing_type",
        "origin",
        "url",
    ]

    assert list(imoveis_vivareal[0]["listing"].keys()) == [
        "displayAddressType",
        "amenities",
        "usableAreas",
        "constructionStatus",
        "listingType",
        "description",
        "title",
        "stamps",
        "createdAt",
        "floors",
        "unitTypes",
        "nonActivationReason",
        "providerId",
        "propertyType",
        "unitSubTypes",
        "unitsOnTheFloor",
        "legacyId",
        "id",
        "portal",
        "unitFloor",
        "parkingSpaces",
        "updatedAt",
        "address",
        "suites",
        "publicationType",
        "externalId",
        "bathrooms",
        "usageTypes",
        "totalAreas",
        "advertiserId",
        "advertiserContact",
        "whatsappNumber",
        "bedrooms",
        "acceptExchange",
        "pricingInfos",
        "showPrice",
        "resale",
        "buildings",
        "capacityLimit",
        "status",
    ]

    imoveis_vivareal[0]["locationId"]

    parsed = clean_data.clean_data(imoveis_vivareal[0])
    parsed.location_id
