import os
import re
import scrapy
from time import sleep
from fetcher.aux import *

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

dir_webdriver = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "chromedriver"
)

# url = "https://www.vivareal.com.br/aluguel/rj/rio-de-janeiro/zona-norte/tijuca/apartamento_residencial/?tipos=apartamento_residencial"
# url = "https://www.vivareal.com.br/imovel/apartamento-2-quartos-tijuca-zona-norte-rio-de-janeiro-com-garagem-70m2-aluguel-RS2470-id-2496556503/"
# fetch(url)
# dir_webdriver = "/mnt/c853ed2a-d0cf-4f28-96bf-f49b1dabdba9/projetos/pessoais/aluguel_imoveis/src/fetcher/chromedriver"
# driver = webdriver.Chrome(dir_webdriver)


class VivaRealSpyder(scrapy.Spider):
    name = "vivarealspyder"

    def __init__(self, url, max_page=1, teste=False):
        super(VivaRealSpyder, self).__init__()
        self.url = url
        self.allowed_domains = [url.split("/")[2]]
        self.start_urls = ["/".join(url.split("/")[:3])]
        self.max_page = int(max_page)
        self.teste = teste
        self.options = Options()
        self.options.add_argument("--disable-extensions")
        self.options.add_argument("--disable-gpu")
        if not teste:
            self.options.add_argument("--headless")

    def parse(self, response):
        page = 1
        botao_proxima_pagina = (
            '//*[@id="js-site-main"]/div[2]/div[1]/section/div[2]/div[2]/div/ul/li[9]'
        )

        with webdriver.Chrome(dir_webdriver, options=self.options) as driver:
            driver.maximize_window()
            get_with_retry(driver, self.url)

            while page <= self.max_page:
                sleep(2)

                response = response.replace(body=driver.page_source)

                url_imoveis = response.xpath(
                    '//*[@data-type="property"]//@href'
                ).getall()

                if self.teste:
                    url_imoveis = url_imoveis[:1]

                for u in url_imoveis:
                    u = self.start_urls[0] + u

                    yield scrapy.Request(
                        u, self.parse_vivareal, cb_kwargs={"url": u, "page": page}
                    )

                if driver.find_element_by_xpath(botao_proxima_pagina).is_enabled():
                    driver.find_element_by_xpath(botao_proxima_pagina).click()
                    page += 1
                else:
                    break

    def parse_vivareal(self, response, url, page):
        with webdriver.Chrome(dir_webdriver, options=self.options) as driver:
            driver.maximize_window()
            get_with_retry(driver, url)

            sucesso, click, tentativa = False, False, 1
            message, glink, lat, lng = "", "", "", ""

            botao_xpath = '//button[@class="map__navigate js-navigate"]'
            glink_iframe_xpath = '//*[@id="js-site-main"]//iframe'
            glink_xpath = '//*[@id="mapDiv"]/div/div/div[8]/div/div/div/div[7]/div/a[contains(@href,"")]'

            response = response.replace(body=driver.page_source)

            while not sucesso and tentativa <= 50:
                if tentativa % 10 == 0:
                    get_with_retry(driver, url)

                botao = get_if_exists(driver, botao_xpath)
                if botao and botao.is_displayed():
                    botao.location_once_scrolled_into_view
                    driver.execute_script("arguments[0].click();", botao)

                iframe = get_if_exists(driver, glink_iframe_xpath)
                if iframe:
                    driver.switch_to.frame(iframe)
                    glink = get_if_exists(driver, glink_xpath)

                    if glink:
                        glink = glink.get_attribute("href")
                        latlng = re.findall("(.\d{2}\.\d{4,6})", glink)
                        if len(latlng) >= 2:
                            lat, lng = float(latlng[0]), float(latlng[1])
                            sucesso = True

                    driver.switch_to.default_content()

                if not sucesso:
                    self.logger.info(f"Tentativa {tentativa} da url '{url}'")
                    sleep(3)
                    tentativa += 1

        if not sucesso:
            self.logger.warn(f"'{url}' não foi pego o lat long")

        r = response.xpath('//*[@id="js-site-main"]/div[2]')

        id_ = re.findall("(id)-(\d{5,10})", url)[0][1]
        tipo = get(response, '//p[@class="price__title"]/text()')
        title = get(response, '//h1[@class="title__title js-title-view"]/text()')
        metragem = get(
            response,
            '//li[@class="features__item features__item--area js-area"]/span/text()',
            True,
        )
        quartos = get(
            response,
            '//li[@class="features__item features__item--bedroom js-bedrooms"]/span/text()',
            True,
        )
        banheiros = get(
            response,
            '//li[@class="features__item features__item--bathroom js-bathrooms"]/span/text()',
            True,
        )
        vagas = get(
            response,
            '//li[@class="features__item features__item--parking js-parking"]/span/text()',
            True,
        )
        endereco = get(response, '//p[@class="title__address js-address"]/text()')
        desc = " ".join(
            response.xpath('//p[@class="description__text"]/text()').getall()
        )

        preco = get(
            response, '//h3[@class="price__price-info js-price-sale"]/text()', True
        )
        condominio = get(
            response,
            '//span[@class="price__list-value condominium js-condominium"]/text()',
            True,
        )
        imagens = response.xpath(
            '//li[@class="carousel__slide js-carousel-item-wrapper"]/img/@src'
        ).getall()

        yield {
            "id": id_,
            "origem": "vivareal",
            "page": page,
            "tipo": tipo,
            "metragem": metragem,
            "quartos": quartos,
            "banheiros": banheiros,
            "vagas": vagas,
            "preco": preco,
            "condominio": condominio,
            "lat": lat,
            "lng": lng,
            "endereco": endereco,
            "title": title,
            "desc": desc,
            "url": url,
            "imagens": imagens,
            # "url_google": glink,
        }
