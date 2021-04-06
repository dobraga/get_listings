import logging
import requests

log = logging.getLogger(__name__)

origin = "vivareal"

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


def list_locations(conf, local):
    api = conf["site"][origin]["api"]
    portal = conf["site"][origin]["portal"]

    headers["referer"] = f"https://www.{origin}.com.br"
    headers["origin"] = f"https://www.{origin}.com.br"
    headers["x-domain"] = f"www.{origin}.com.br"

    base_url = f"https://{api}/v3/locations"

    query = {
        "q": local,
        "fields": "neighborhood",
        "portal": portal,
        "size": "6",
    }

    try:
        r = requests.get(base_url, params=query, headers=headers)
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        log.error(e)
        raise e

    locations = r.json()["neighborhood"]["result"]["locations"]

    locations = [l["address"] for l in locations]

    locations = list({v["locationId"]: v for v in locations}.values())

    return locations
