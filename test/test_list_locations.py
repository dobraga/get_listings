from backend.location import list_locations


def test_list_locations():
    locations = list_locations("tijuca")

    assert list(locations.keys()) == [
        "Tijuca, Rio de Janeiro - RJ",
        "Tijuca, Teresopolis - RJ",
    ]

    assert list(locations["Tijuca, Rio de Janeiro - RJ"].keys()) == [
        "city",
        "stateAcronym",
        "zone",
        "locationId",
        "state",
        "neighborhood",
    ]
