import os
import re
import scrapy
from json import loads
from time import sleep
from retry import retry

from selenium import webdriver

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

# url = "https://www.zapimoveis.com.br/imovel/aluguel-apartamento-3-quartos-com-armario-de-cozinha-tijuca-zona-norte-rio-de-janeiro-rj-98m2-id-2484308793/"
# url = "https://www.vivareal.com.br/imovel/apartamento-2-quartos-tijuca-zona-norte-rio-de-janeiro-56m2-venda-RS290000-id-2489298094/?__vt=lgpd:a"
# url = "https://www.vivareal.com.br/aluguel/rj/rio-de-janeiro/zona-norte/tijuca/apartamento_residencial/?__vt=lgpd:c#onde=BR-Rio_de_Janeiro-NULL-Rio_de_Janeiro-Zona_Norte-Tijuca&tipos=apartamento_residencial"
# fetch(url)
# dir_webdriver = "/mnt/c853ed2a-d0cf-4f28-96bf-f49b1dabdba9/projetos/pessoais/aluguel_imoveis/src/fetcher/chromedriver"
# driver = webdriver.Chrome(dir_webdriver)

dir_webdriver = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "chromedriver"
)

options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")


def get(r, xpath, to_int=False):
    return parse_int(r.xpath(xpath).get(), to_int)


def parse_int(s, to_int=False):
    try:
        s = s.strip()
        if to_int:
            s = "".join(re.findall("[0-9|\,]", s))
            s = s.replace(",", ".")
        if s.isdigit():
            return int(s)
        else:
            return s
    except:
        if to_int:
            return 0
        else:
            return ""


class ImoveisSpyder(scrapy.Spider):
    name = "imoveisspyder"

    def __init__(self, url, max_page=1):
        super(ImoveisSpyder, self).__init__()
        self.url = url
        self.allowed_domains = [url.split("/")[2]]
        self.start_urls = ["/".join(url.split("/")[:3])]
        self.max_page = int(max_page)

    def parse(self, response):
        # //*[@id="app"]/section/div/div[2]/section/ul/li[7]/button zap
        # //*[@id="js-site-main"]/div[2]/div[1]/section/div[2]/div[2]/div/ul/li[9] vivareal

        for page in range(1, self.max_page + 1):
            url = self.url + str(page)
            yield scrapy.Request(
                url, self.parse_page, cb_kwargs={"url": url, "page": page}
            )

    def parse_page(self, response, url, page):
        with webdriver.Chrome(dir_webdriver) as driver:  # , options=options
            driver.maximize_window()
            driver.get(url)
            sleep(2)

            if "vivareal" in self.start_urls[0]:
                response = response.replace(body=driver.page_source)

                url_imoveis = response.xpath(
                    '//*[@data-type="property"]//@href'
                ).getall()

                self.logger.warn(f"Página {page}")

            elif "zap" in self.start_urls[0]:
                botoes = driver.find_elements_by_xpath('//*[@class="card-container"]')
                url_imoveis = []

                for botao in botoes:
                    botao.click()
                    sleep(1)
                    driver.switch_to.window(driver.window_handles[-1])
                    print(driver.current_url)
                    url_imoveis.append(driver.current_url)
                    driver.switch_to.window(driver.window_handles[0])

        print(url_imoveis)
        for u in url_imoveis:
            if "vivareal" in self.start_urls[0]:
                u = self.start_urls[0] + u

                yield scrapy.Request(
                    u, self.parse_vivareal, cb_kwargs={"url": u, "page": page}
                )

            elif "zap" in self.start_urls[0]:
                yield scrapy.Request(
                    u, self.parse_zap, cb_kwargs={"url": u, "page": page}
                )

    def parse_vivareal(self, response, url, page):
        with webdriver.Chrome(dir_webdriver, options=options) as driver:
            driver.maximize_window()
            driver.get(url)
            sucesso, click, tentativa = False, False, 1
            message, glink, lat, lng = "", "", "", ""

            botao_xpath = '//*[@id="js-site-main"]/div[3]/section/div/button[1]'
            glink_xpath = (
                '//*[@id="js-site-main"]/div[3]/section/div/div/article/iframe'
            )

            response = response.replace(body=driver.page_source)

            while not sucesso and tentativa <= 10:

                botao = driver.find_element_by_xpath(botao_xpath)
                if botao.is_displayed():
                    botao.location_once_scrolled_into_view
                    sleep(1)
                    botao.click()

                sleep(2)

                try:
                    if driver.find_elements_by_xpath(glink_xpath):
                        driver.switch_to.frame(
                            driver.find_element_by_xpath(glink_xpath)
                        )

                        glink = driver.find_element_by_xpath(
                            '//*[@id="mapDiv"]/div/div/div[8]/div/div/div/div[7]/div/a[contains(@href,"")]'
                        ).get_attribute("href")

                except:
                    pass

                finally:
                    driver.switch_to.default_content()

                if glink:
                    latlng = re.findall("(.\d{2}\.\d{4,6})", glink)
                    if len(latlng) >= 2:
                        lat, lng = float(latlng[0]), float(latlng[1])
                        sucesso = True

                if not sucesso:
                    self.logger.warn(f"Tentativa {tentativa} da url '{url}'")
                    sleep(tentativa)
                    tentativa += 1

        r = response.xpath('//*[@id="js-site-main"]/div[2]')

        id_ = re.findall("(id)-(\d{10})", url)[0][1]
        tipo = get(r, ".//div[2]/div[1]/div/div[1]/p//text()")
        title = get(r, ".//div[1]/div[1]/section/div/h1//text()")
        metragem = get(r, ".//div[1]/div[2]/ul/li[1]/span//text()", True)
        quartos = get(r, ".//div[1]/div[2]/ul/li[2]/span//text()", True)
        banheiros = get(r, ".//div[1]/div[2]/ul/li[3]/span//text()", True)
        vagas = get(r, ".//div[1]/div[2]/ul/li[4]/span//text()", True)
        endereco = get(r, ".//div[1]/div[1]/section/div/div/p//text()")
        desc = get(r, ".//div[1]/div[4]/div[1]/div/div/p//text()")
        preco = get(r, ".//div[2]/div[1]/div/div[1]/h3//text()", True)
        condominio = get(
            r, ".//div[2]/div[1]/div/div[2]/ul/li[1]/span[2]//text()", True
        )
        imagens = response.xpath(
            '//*[@id="js-site-main"]/div[1]/div[1]/a/ul/li//@src'
        ).getall()

        yield {
            "id_": id_,
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
            "url_google": glink,
        }

    def parse_zap(self, response, url, page):
        with webdriver.Chrome(dir_webdriver) as driver:  # , options=options
            driver.maximize_window()
            driver.get(url)
            sucesso, click, tentativa = False, False, 1
            message, glink, lat, lng = "", "", "", ""

            botao_xpath = ".//article[1]/div/div[1]/div[1]/p/button/span[2]"
            glink_xpath = '//*[@id="listing-map"]/article/iframe'

            response = response.replace(body=driver.page_source)

            while not sucesso and tentativa <= 10:
                try:
                    botao = driver.find_element_by_xpath(botao_xpath)
                    botao.click()
                except:
                    pass

                try:
                    if driver.find_elements_by_xpath(glink_xpath):
                        driver.switch_to.frame(
                            driver.find_element_by_xpath(glink_xpath)
                        )

                        glink = driver.find_element_by_xpath(
                            '//*[@id="mapDiv"]/div/div/div[8]/div/div/div/div[7]/div/a[contains(@href,"")]'
                        ).get_attribute("href")

                except:
                    pass

                finally:
                    driver.switch_to.default_content()

                if glink:
                    latlng = re.findall("(.\d{2}\.\d{4,6})", glink)
                    if len(latlng) >= 2:
                        lat, lng = float(latlng[0]), float(latlng[1])
                        sucesso = True

                if not sucesso:
                    self.logger.warn(f"Tentativa {tentativa} da url '{url}'")
                    sleep(tentativa)
                    tentativa += 1

        r = response.xpath('//*[@id="app"]/section')

        id_ = re.findall("(id)-(\d{10})", url)[0][1]
        tipo = get(r, ".//article[1]/div/div[1]/div[1]/p/span[2]/text()")
        title = get(r, ".//article[1]/h1/strong/text()")
        metragem = get(
            r, ".//article[1]/div/div[1]/div[2]/ul/li[1]/span[2]/text()", True,
        )
        quartos = get(
            r, ".//article[1]/div/div[1]/div[2]/ul/li[2]/span[2]/text()", True,
        )
        banheiros = get(
            r, ".//article[1]/div/div[1]/div[2]/ul/li[4]/span[2]/text()", True,
        )
        vagas = get(r, ".//article[1]/div/div[1]/div[2]/ul/li[3]/span[2]/text()", True,)
        endereco = get(r, ".//article[1]/div/div[1]/div[1]/p/button/span[2]/text()",)
        desc = get(r, ".//div[2]/article/div[1]/aside[2]/div/div/div/text()",)
        preco = get(
            r, ".//article[1]/div/div[1]/div[2]/div/ul[1]/li[1]/strong/text()", True,
        )
        condominio = get(
            r, ".//article[1]/div/div[1]/div[2]/div/ul[2]/li[1]/span", True,
        )
        imagens = response.xpath(
            '//*[@id="listing-carousel"]/section/ul/li//@src'
        ).getall()

        yield {
            "id_": id_,
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
            "url_google": glink,
        }
