from concurrent.futures import ProcessPoolExecutor, as_completed
from requests import Session, get
from flask import current_app
from lxml import html
import pandas as pd
import logging

from listings.models import Metro
from listings.extensions.serializer import MetroSchema

base_url = "https://pt.wikipedia.org"
ms = MetroSchema(many=True)
log = logging.getLogger(__name__)


def list_estacoes(urls: list) -> set:
    output = []

    for url in urls:
        # parse de uma única URL
        tree_home = html.document_fromstring(get(url).text)
        base_xpath = '(//tr/th[contains(text(), "erminais")]/../..)[1]/tr/td[1]//a//'

        linhas = tree_home.xpath(base_xpath + "@title")
        url_linhas = tree_home.xpath(base_xpath + "@href")

        for linha, url_linha in zip(linhas, url_linhas):
            # parse de uma linha de metro/trêm
            url_linha = base_url + url_linha

            tree_linha = html.document_fromstring(get(url_linha).text)
            url_estacoes = tree_linha.xpath(
                '//tr/td/a[contains(@href, "wiki/Esta")]/@href'
            )
            output += [(linha, base_url + u) for u in url_estacoes]

    return set(output)


def fetch(session, url_estacao) -> tuple:
    with session.get(url_estacao) as resp:
        tree_estacao = html.document_fromstring(resp.text)

        estacao = tree_estacao.xpath('//*[@id="firstHeading"]/text()')[0]
        url_latlng = tree_estacao.xpath(
            '//a[contains(@href, "tools.wmflabs.org")]/@href'
        )

        if len(url_latlng) > 0:
            tree_latlng = html.document_fromstring(get(url_latlng[0]).text)

            lat, lng = tree_latlng.xpath('//*[contains(@class, "geo")]/span/text()')
            lat, lng = float(lat), float(lng)

            return estacao, lat, lng

        return None, None, None


def get_metro(uf: str, config: dict, db):
    uf = uf.lower()
    urls = config["METRO_TREM"].get(uf)

    if urls is None:
        log.warning(f"not found metro/train urls for {uf}")
        return pd.DataFrame()
    urls = urls["urls"]

    metros = Metro.query.filter_by(uf=uf).all()

    if metros:
        return pd.DataFrame(ms.dump(metros))

    estacoes = list_estacoes(urls)

    with Session() as session:
        with ProcessPoolExecutor() as executor:
            futures = {
                executor.submit(fetch, session, url_estacao): (
                    linha,
                    url_estacao,
                )
                for linha, url_estacao in estacoes
            }

            for future in as_completed(futures):
                linha, url_estacao = futures[future]
                estacao, lat, lng = future.result()

                if lat:
                    metro = Metro(
                        uf=uf,
                        linha=linha,
                        estacao=estacao,
                        lat=lat,
                        lng=lng,
                        url=url_estacao,
                    )

                    db.session.add(metro)

        db.session.commit()

    return pd.DataFrame(ms.dump(metros))
