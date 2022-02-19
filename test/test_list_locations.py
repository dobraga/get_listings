from backend.location import list_locations


def test_list_locations():
    locations = list_locations("tijuca")

    assert "Tijuca, Rio de Janeiro - RJ" in list(locations.keys())

    assert list(locations["Tijuca, Rio de Janeiro - RJ"].keys()) == [
        "city",
        "stateAcronym",
        "zone",
        "locationId",
        "state",
        "neighborhood",
    ]
