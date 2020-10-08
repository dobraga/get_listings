import os
import re
import scrapy
from time import sleep
from fetcher.aux import *

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import StaleElementReferenceException

dir_webdriver = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "chromedriver"
)

from pyvirtualdisplay import Display

# url = "https://www.zapimoveis.com.br/aluguel/apartamentos/rj+rio-de-janeiro+zona-norte+tijuca/?onde=,Rio%20de%20Janeiro,Rio%20de%20Janeiro,Zona%20Norte,Tijuca,,,neighborhood,BR%3ERio%20de%20Janeiro%3ENULL%3ERio%20de%20Janeiro%3EZona%20Norte%3ETijuca,-22.923715,-43.258467&pagina=9&tipo=Im%C3%B3vel%20usado&tipoUnidade=Residencial,Apartamento&transacao=Aluguel"
# url = "https://www.zapimoveis.com.br/imovel/venda-apartamento-2-quartos-com-elevador-tijuca-zona-norte-rio-de-janeiro-rj-78m2-id-2495667753/"
# fetch(url)
# dir_webdriver = "/mnt/c853ed2a-d0cf-4f28-96bf-f49b1dabdba9/projetos/pessoais/aluguel_imoveis/src/fetcher/chromedriver"
# driver = webdriver.Chrome(dir_webdriver)


class ZapSpyder(scrapy.Spider):
    name = "zapspyder"

    def __init__(self, url, max_page=1, teste=False):
        super(ZapSpyder, self).__init__()
        self.url = url
        self.allowed_domains = [url.split("/")[2]]
        self.start_urls = ["/".join(url.split("/")[:3])]
        self.max_page = int(max_page)
        self.visible = 1 if teste else 0
        self.options = Options()
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--disable-extensions")
        self.teste = teste
        if not teste:
            self.options.add_argument("--headless")

    def parse(self, response):
        page = 0
        botao_proxima_pagina = '//button[@aria-label="Próxima Página"]'

        with Display(visible=self.visible, size=(1600, 1024)):
            with webdriver.Chrome(dir_webdriver) as driver:
                driver.maximize_window()
                get_with_retry(driver, self.url)

                for page in range(1, self.max_page + 1):
                    href = f'//a[@href="?pagina={page}"]'

                    proxima_pagina = get_if_exists(driver, href)
                    if proxima_pagina:
                        proxima_pagina.click()
                        yield scrapy.Request(
                            driver.current_url,
                            self.parse_page,
                            cb_kwargs={"url": driver.current_url, "page": page},
                        )

    def parse_page(self, response, url, page):
        with webdriver.Chrome(dir_webdriver, options=self.options) as driver:
            driver.maximize_window()
            get_with_retry(driver, url)

            xpath_botoes = '//*[@class="card-container"]'

            if self.teste:
                qtd_botoes = 1
            else:
                qtd_botoes = len(driver.find_elements_by_xpath(xpath_botoes))

            links = []

            for idx in range(qtd_botoes):
                tentativa = 1
                u = url

                while url == u:
                    if tentativa % 20 == 0:
                        get_with_retry(driver, url)

                    botao = driver.find_elements_by_xpath(xpath_botoes)[idx]
                    try:
                        botao.click()
                        # driver.execute_script("arguments[0].click();", botao)
                        driver.switch_to.window(driver.window_handles[-1])
                        sleep(1)
                        u = driver.current_url
                    except StaleElementReferenceException:
                        pass

                    tentativa += 1

                links.append(u)
                driver.switch_to.window(driver.window_handles[0])

        for link in links:
            yield scrapy.Request(
                link, self.parse_zap, cb_kwargs={"url": link, "page": page}
            )

    def parse_zap(self, response, url, page):
        with Display(visible=self.visible, size=(1600, 1024)):
            with webdriver.Chrome(dir_webdriver) as driver:
                driver.maximize_window()
                get_with_retry(driver, url)
                sucesso, click, tentativa = False, False, 1
                message, glink, lat, lng, imagens = "", "", "", "", ""

                botao_xpath = ".//article[1]/div/div[1]/div[1]/p/button/span[2]"
                glink_iframe_xpath = '//*[@id="listing-map"]/article/iframe'
                glink_xpath = '//*[@id="mapDiv"]/div/div/div[8]/div/div/div/div[7]/div/a[contains(@href,"")]'
                botao_fotos_xpath = "//li[1]/button"

                response = response.replace(body=driver.page_source)

                while not sucesso and tentativa <= 50:
                    if tentativa % 10 == 0:
                        get_with_retry(driver, url)

                    try:
                        botao = get_if_exists(driver, botao_xpath)
                        if botao:
                            botao.click()
                            sleep(2)
                    except:
                        pass

                    iframe = get_if_exists(driver, glink_iframe_xpath)
                    if iframe:
                        driver.switch_to.frame(iframe)
                        sleep(3)
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

                botao_fotos = get_if_exists(driver, botao_fotos_xpath)
                if botao_fotos:
                    driver.execute_script("arguments[0].click();", botao_fotos)
                    imagens = driver.find_elements_by_xpath(
                        '//*[@id="listing-carousel"]/section/ul/li/img[contains(@src,"")]'
                    )
                    imagens = [imagen.get_attribute("src") for imagen in imagens]

        if not sucesso:
            self.logger.warn(f"'{url}' não foi pego o lat long")

        r = response.xpath('//*[@id="app"]/section')

        id_ = re.findall("(id)-(\d{5,10})", url)[0][1]

        tipo = get(r, ".//article[1]/div/div[1]/div[1]/p/span/text()")
        title = get(r, ".//article[1]/h1/strong/text()")
        metragem = get(
            response,
            '//li[@class="feature__item text-regular js-areas"]//text()',
            True,
        )

        quartos = get(
            response,
            '//li[@class="feature__item text-regular js-bedrooms"]//text()',
            True,
        )

        banheiros = get(
            response,
            '//li[@class="feature__item text-regular js-bathrooms"]//text()',
            True,
        )

        vagas = get(
            response,
            '//li[@class="feature__item text-regular js-parking-spaces"]//text()',
            True,
        )

        endereco = get(r, ".//article[1]/div/div[1]/div[1]/p/button/span[2]/text()",)
        desc = " ".join(
            response.xpath(
                '//div[@class="amenities__description text-regular text-margin-zero"]/text()'
            ).getall()
        )
        preco = get(
            response,
            '//li[@class="price__item--main text-regular text-regular__bolder"][last()]/strong/text()',
            True,
        )

        condominio = get(
            response,
            '//li[@class="price__item condominium color-dark text-regular"]/span/text()',
            True,
        )

        yield {
            "id": id_,
            "origem": "zap",
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
