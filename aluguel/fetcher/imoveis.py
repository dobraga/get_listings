from concurrent.futures import ProcessPoolExecutor
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from os.path import join, exists
from datetime import datetime
from time import sleep
from math import ceil
import pandas as pd
import jsonlines
import re

try:
    from .aux import *
    from ..util import str_flat
    from ..util.context import RemoteLogger
except:
    from aluguel.fetcher.aux import *
    from aluguel.util import str_flat
    from aluguel.util.context import RemoteLogger



class Imoveis:
    def __init__(self, conf, log):
        self.conf = conf
        self.log = log
        self.max_page = int(conf["max_page"])
        self.output = conf.get("output") or join(conf["dir_input"], "imoveis.jsonlines")

        self.log.info(f"init: Será salvo no arquivo: {self.output}")
        if not exists(self.output):
            with open(self.output, 'w'): pass

        self.urls_extraidas = []
        if exists(self.output):
            df = pd.read_json(self.output, lines=True)
            if "url" in df.columns:
                self.urls_extraidas = df.url.to_list()

        self.log.info("run: Criando url iniciais")
        with ProcessPoolExecutor() as exe:
            base_url = exe.map(self.make_url, conf["site"])
            self.base_url = list(base_url).copy()
        self.log.info(f"init: Urls iniciais:\n{self.base_url}")


    def run(self):
        """
        Run all proccess to get properties
        """
        with ProcessPoolExecutor() as exe:
            self.log.info("run: Criando url das páginas")
            paginas = exe.map(self.get_paginas, self.base_url)
            paginas = flat(list(paginas).copy())
            self.log.info(f"run: Url de {len(paginas)} páginas criadas")

            self.log.info("run: Buscando url dos imóveis")
            imoveis = exe.map(self.get_imoveis, paginas)
            imoveis = flat(list(imoveis).copy())
            filtrados = len(list(filter(lambda x: x in self.urls_extraidas, imoveis)))
            self.log.info(f"run: Total de {len(imoveis)} urls de imóveis, porem {filtrados} já extraídos")

            imoveis = list(filter(lambda x: x not in self.urls_extraidas, imoveis))
            self.log.info(f"run: Buscando um total de {len(imoveis)} imóveis")

            return list(exe.map(self.parse_imovel, imoveis))



    def make_url(self, site):
        """
        Return the base url to get pages
        """
        with RemoteLogger(self.conf["webdriver"], self.log, "make_url", site) as driver:
            url = self.conf[site]["url"]
            get_sleep(driver, url)

            print(driver.session_id)

            local = self.conf["local"]
            valor_minimo = self.conf.get("valor_minimo", -1)
            valor_maximo = self.conf.get("valor_maximo", -1)
            tipo_contrato = self.conf[site]["tipo_contrato"]
            tipo_propriedade = self.conf[site]["tipo_propriedade"]

            # popup de cookies
            pass_cookie(driver)

            # Seleciona o tipo de contrato
            tipo_contrato_xpath = str_flat(f'''
                //option[contains(text(), "{tipo_contrato}")] |
                //button[@title="{tipo_contrato}"]
            ''')
            driver.find_element(By.XPATH, tipo_contrato_xpath).click()

            # Seleciona o tipo da propriedade
            tipo_propriedade_xpath = str_flat('''
                //select[@class="js-select-type"] |
                //select[contains(@class, "l-select__item")]
            ''')
            driver.find_element(By.XPATH, tipo_propriedade_xpath).click()

            tipo_propriedade_xpath = str_flat(f'''
                //option[contains(text(), "{tipo_propriedade}")] |
                //option[contains(text(), "{tipo_propriedade}")]
            ''')
            driver.find_element(By.XPATH, tipo_propriedade_xpath).click()

            # Seleciona o local
            local_xpath = str_flat('''
                //input[@id="filter-location-search-input"] |
                //input[contains(@class, "js-typeahead-input")]
            ''')

            select_local = driver.find_element(By.XPATH, local_xpath)
            select_local.send_keys(local)
            sleep(3)
            select_local.send_keys(Keys.ENTER)

            # Buscar
            if "zap" in url:
                buscar_xpath = str_flat('''
                    //button[contains(@class, "button-primary--standard")] |
                    //button[@data-qa="search-button"]
                ''')
                driver.find_element(By.XPATH, buscar_xpath).click()

            # Define range de preco
            if valor_minimo > 0 or valor_maximo > 0:
                preco_xpath = str_flat('''
                    //button[contains(@class, "js-price-toggle")] | 
                    //div[contains(@class, "js-price-range")]
                ''')
                preco = driver.find_element(By.XPATH, preco_xpath)

                url = driver.current_url

                preco.click()

                if valor_minimo > 0:
                    preco_min = get_if_exists(
                        driver, 
                        str_flat('''
                            //input[contains(@class, "js-price-min")] |
                            //input[@id="filter-range-from-price"]
                        ''')
                    )
                    preco_min.send_keys(valor_minimo)

                if valor_maximo > 0:
                    preco_max = get_if_exists(
                        driver, 
                        str_flat('''
                            //input[contains(@class, "js-price-max")] |
                            //input[@id="filter-range-to-price"]
                        ''')
                    )
                    preco_max.send_keys(valor_maximo)

                while url == driver.current_url:
                    preco.click()
                    sleep(1)

            return driver.current_url



    def get_paginas(self, url:str) -> list:
        """
        Return the url pages
        """
        with RemoteLogger(self.conf["webdriver"], self.log, "get_paginas", url) as driver:
            get_sleep(driver, url)

            qtd_imoveis_total = get(driver, "//h1")
            qtd_imoveis_total = re.match("([^\s]+)", qtd_imoveis_total).group()
            qtd_imoveis_total = parse_int(qtd_imoveis_total, True)

            qtd_imoveis_pagina = len(
                driver.find_elements(
                    By.XPATH, 
                    str_flat('''
                        //a[contains(@class, "js-card-title")] |
                        //div[@class="card-container"]
                    ''')
                )
            )

            qtd_paginas = ceil(qtd_imoveis_total/qtd_imoveis_pagina)
            if self.max_page > 0:
                qtd_paginas = min(qtd_paginas, self.max_page)

            url_page = url + "&pagina={}"

            paginas = [url_page.format(page) for page in range(1, qtd_paginas+1)]

        return paginas



    def get_imoveis(self, url:str) -> list:
        """
        Return the properties link
        """
        def click_get_link(driver, botao):
            botao.click()
            driver.switch_to.window(driver.window_handles[1])
            _ = get( driver, '//*[contains(@class,"main__info--title")]')
            sleep(0.5)
            u = driver.current_url

            driver.close()
            driver.switch_to.window(driver.window_handles[0])

            return u


        with RemoteLogger(self.conf["webdriver"], self.log, "get_imoveis", url) as driver:
            get_sleep(driver, url, time_sleep=5)

            pass_cookie(driver)

            botoes_xpath = str_flat('''
                //a[contains(@class, "js-card-title")] |
                //div[@class="card-container"]
            ''')
            botoes = driver.find_elements(By.XPATH, botoes_xpath)

            links = [
                botao.get_attribute("href") or click_get_link(driver, botao) 
                for botao in botoes
            ]

            return links



    def parse_imovel(self, url:str, mode:str = "w") -> dict:
        """
        Return the property information
        """
        with RemoteLogger(self.conf["webdriver"], self.log, "parse_imovel", url) as driver:
            session_id = driver.session_id
            get_sleep(driver, url, time_sleep_ini=5 if "zap" in url else 0)
            pass_cookie(driver)

            id_ = re.findall("(id)-(\d{5,10})", url)[0][1]

            tipo_xpath = str_flat('''
                //*[@class="price__title"] |
                //*[contains(@class,"info__business-type")]
            ''')
            tipo = driver.find_element(By.XPATH, tipo_xpath).text

            title = get(
                driver, 
                str_flat('''
                    //*[contains(@class,"js-title-view")] |
                    //*[contains(@class,"main__info--title")]
                ''')
            )

            endereco = get(
                driver, 
                str_flat('''
                    //*[contains(@class,"title__address")] |
                    //*[contains(@class, "info__map-link")]
                ''')
            )

            metragem = get(
                driver, 
                str_flat('''
                    //*[contains(@class,"features__item--area")]/span |
                    //*[contains(@class,"js-areas")]/span[2]
                '''),
                True
            )

            quartos = get(
                driver, 
                str_flat('''
                    //*[contains(@class,"features__item--bedroom")]/span |
                    //*[contains(@class,"js-bedrooms")]/span[2]
                '''),
                True
            )

            banheiros = get(
                driver, 
                str_flat('''
                    //*[contains(@class,"features__item--bathroom")]/span |
                    //*[contains(@class,"js-bathrooms")]/span[2]
                '''),
                True
            )

            vagas = get(
                driver, 
                str_flat('''
                    //*[contains(@class,"features__item--bedroom")]/span |
                    //*[contains(@class,"js-parking-spaces")]/span[2]
                '''),
                True
            )

            desc = driver.find_elements(
                By.XPATH,
                str_flat('''
                    //*[@class="description__text"] |
                    //*[contains(@class,"amenities__description")]
                ''')
            )
            desc = " ".join([d.text for d in desc])

            preco = get(
                driver, 
                str_flat('''
                    //*[contains(@class,"js-price-sale")][last()] |
                    //*[contains(@class,"price__item--main")][last()]
                '''),
                True
            )

            condominio = get(
                driver, 
                str_flat('''
                    //*[contains(@class,"js-condominium")] |
                    //*[contains(@class,"condominium")]/span[contains(@class,"price__value")]
                '''),
                True
            )

            img_xpath = str_flat('''
                //li[contains(@class,"carousel__slide")]/img |
                //li[contains(@class,"carousel__item")]/img
            ''')

            try:
                imagens = driver.find_elements(By.XPATH, img_xpath)

                imagens = [img.get_attribute("src") for img in imagens]
            except TimeoutException:
                imagens = []
                self.log.warning(f"parse_imovel: {session_id}: {url}: sem imagens")

            sucesso, tentativa = False, 0
            glink, lat, lng = "", "", ""

            botao_xpath = str_flat('''
                //button[contains(@class,"map__navigate")] |
                //button[contains(@class,"info__map-link")]
            ''')
            glink_iframe_xpath = str_flat('''
                //*[@id="listing-map"]/article/iframe |
                //*[@id="js-site-main"]//iframe
            ''')
            glink_xpath = str_flat('''
                //*[@id="mapDiv"]/div/div/div[8]/div/div/div/div[7]/div/a[contains(@href,"")] |
                //*[@id="mapDiv"]//div[@class="google-maps-link"]/a[contains(@href,"")]
            ''')


            while not sucesso and tentativa <= 14:            
                try:
                    driver.find_element(By.XPATH, botao_xpath).click()
                    self.log.debug(f"parse_imovel: {session_id}: {url}: abriu o mapa")
                except:
                    self.log.debug(f"parse_imovel: {session_id}: {url}: não conseguiu abrir o mapa")

                try:
                    iframe = driver.find_element(By.XPATH, glink_iframe_xpath)
                    driver.switch_to.frame(iframe)
                    self.log.debug(f"parse_imovel: {session_id}: {url}: entrou no iframe")
                except:
                    self.log.debug(f"parse_imovel: {session_id}: {url}: não conseguiu entrar no iframe")

                try:
                    glink = driver.find_element(By.XPATH, glink_xpath).get_attribute("href")
                    latlng = re.findall("(.\d{2}\.\d{4,6})", glink)
                    lat, lng = float(latlng[0]), float(latlng[1])
                    sucesso = True
                except:
                    pass
                
                if not sucesso:
                    tentativa += 1
                    self.log.warning(f"parse_imovel: {session_id}: {url}: não conseguiu pegar latlong na tentativa {tentativa}")
                    driver.switch_to.default_content()
                    driver.switch_to.window(driver.window_handles[0])

                if tentativa % 5 == 0:
                    get_sleep(driver, url, 5)
                    pass_cookie(driver)

            if sucesso:
                self.log.debug(f"parse_imovel: {session_id}: {url}: latlong OK")
            else:
                self.log.warning(f"parse_imovel: {session_id}: {url}: latlong não encontrada")

            origem = "zap" if "zap" in url else "vivareal"

            line = {
                "extraido": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "id": origem + "_" + id_,
                "origem": origem,
                "tipo": "Aluguel" if "ALUG" in tipo.upper() else "Compra",
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

            if "w" in mode:
                with jsonlines.open(self.output, "a") as writer:
                    writer.write(line)
            return line

