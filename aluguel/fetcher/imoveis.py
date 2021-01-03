from concurrent.futures import ProcessPoolExecutor
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver import Remote
from os.path import join, exists
from retry import retry
from time import sleep
from math import ceil
import pandas as pd
from .aux import *
import jsonlines
import re

class Imoveis:
    def __init__(self, conf):
        self.conf = conf
        self.max_page = int(conf["max_page"])
        self.output = conf.get("output") or join(conf["dir_input"], "imoveis.jsonlines")
        print("Será salvo no arquivo: ", self.output)
        if not exists(self.output):
            with open(self.output, 'w'): pass

        self.base_url = [self.make_url(conf, site) for site in conf["site"]]

        self.urls_extraidas = []
        if exists(self.output):
            df = pd.read_json(self.output, lines=True)
            if "url" in df.columns:
                self.urls_extraidas = df.url.to_list()

        print(f"Páginas iniciais: {self.base_url} \n")


    def run(self):
        with ProcessPoolExecutor() as exe:
            base_url = self.base_url
            paginas = exe.map(self.get_paginas, base_url)
            paginas = flat(list(paginas))
            print(f"Buscando um total de {len(paginas)} páginas")

            imoveis = exe.map(self.get_imoveis, paginas)
            imoveis = flat(list(imoveis))
            imoveis = list(filter(lambda x: x not in self.urls_extraidas, imoveis))
            print(f"Buscando um total de {len(imoveis)} imóveis")

            return list(exe.map(self.parse_imovel, imoveis))
    

    def make_url(self, conf, site):
        with Remote(**self.conf["webdriver"]) as driver:
            driverw = WebDriverWait(driver, 20)
            url = conf[site]["url"]
            local = conf["local"]
            valor_minimo = conf.get("valor_minimo", 0)
            valor_maximo = conf.get("valor_maximo", 1000000)
            tipo_contrato = conf[site]["tipo_contrato"]
            tipo_propriedade = conf[site]["tipo_propriedade"]

            get_sleep(driver, url)


            # popup de cookies
            pass_cookie(driver)


            # Seleciona o tipo de contrato
            tipo_contrato_xpath = str_flat(f'''
                //option[contains(text(), "{tipo_contrato}")] |
                //button[@title="{tipo_contrato}"]
            ''')
            driverw.until(
                EC.element_to_be_clickable((By.XPATH, tipo_contrato_xpath))
            ).click()


            # Seleciona o tipo da propriedade
            tipo_propriedade_xpath = str_flat('''
                //select[@class="js-select-type"] |
                //select[contains(@class, "l-select__item")]
            ''')
            driverw.until(
                EC.element_to_be_clickable((By.XPATH, tipo_propriedade_xpath))
            ).click()


            tipo_propriedade_xpath = str_flat(f'''
                //option[contains(text(), "{tipo_propriedade}")] |
                //option[contains(text(), "{tipo_propriedade}")]
            ''')
            driverw.until(
                EC.element_to_be_clickable((By.XPATH, tipo_propriedade_xpath))
            ).click()


            # Seleciona o local
            local_xpath = str_flat('''
                //input[@id="filter-location-search-input"] |
                //input[contains(@class, "js-typeahead-input")]
            ''')

            select_local = get_if_exists(driver, local_xpath)
            select_local.send_keys(local)
            sleep(3)
            select_local.send_keys(Keys.ENTER)


            # Buscar
            buscar_xpath = str_flat('''
                //button[contains(@class, "button-primary--standard")] |
                //button[@data-qa="search-button"]
            ''')

            buscar = get_if_exists(driver, buscar_xpath)

            if buscar:
                buscar.click()


            # Define range de preco
            preco_xpath = str_flat('''
                //button[contains(@class, "js-price-toggle")] | 
                //div[contains(@class, "js-price-range")]
            ''')

            preco = driverw.until(
                EC.visibility_of_element_located((By.XPATH, preco_xpath))
            )

            if preco:
                url = driver.current_url

                preco.click()

                preco_min = get_if_exists(
                    driver, 
                    str_flat('''
                        //input[contains(@class, "js-price-min")] |
                        //input[@id="filter-range-from-price"]
                    ''')
                )
                preco_min.send_keys(valor_minimo)

                preco_max = get_if_exists(
                    driver, 
                    str_flat('''
                        //input[contains(@class, "js-price-max")] |
                        //input[@id="filter-range-to-price"]
                    ''')
                )
                preco_max.send_keys(valor_maximo)

                preco.click()

                while url == driver.current_url:
                    sleep(1)

                return driver.current_url



    def get_paginas(self, url:str) -> list:
        with Remote(**self.conf["webdriver"]) as driver:
            get_sleep(driver, url)

            qtd_imoveis_total = get(driver, "//h1")
            qtd_imoveis_total = parse_int(re.match("([^\s]+)", qtd_imoveis_total).group(), True)

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
        with Remote(**self.conf["webdriver"]) as driver:
            get_sleep(
                driver, url, time_sleep=5,
                time_sleep_ini=5 if "zap" in url else 0
            )

            botoes = driver.find_elements(
                By.XPATH,
                str_flat('''
                    //a[contains(@class, "js-card-title")] |
                    //div[@class="card-container"]
                ''')
            )

            try:
                links = [botao.get_attribute("href") for botao in botoes]
            except:
                links = []

            if not all(links):
                def click_get_link(driver, xpath, idx):
                    tentativa = 1
                    u = driver.current_url

                    while driver.current_url == u:
                        if tentativa % 20 == 0:
                            print(f"retry {tentativa}: {url}")
                            get_sleep(driver, url)

                        botao = driver.find_elements_by_xpath(xpath)[idx]
                        try:
                            botao.click()
                            driver.switch_to.window(driver.window_handles[1])
                            sleep(1)
                            u = driver.current_url
                        finally:
                            sleep(2)

                        tentativa += 1
                        driver.switch_to.window(driver.window_handles[0])

                    return u

                links = [
                    click_get_link(driver, '//div[@class="card-container"]', idx)
                    for idx in range(len(botoes))
                ]

            return links


    @retry(tries=5)
    def parse_imovel(self, url:str, mode="w") -> dict:
        with Remote(**self.conf["webdriver"]) as driver:
            try:
                session_id = driver.session_id
                get_sleep(driver, url, time_sleep_ini=5 if "zap" in url else 0)
                driverw = WebDriverWait(driver, 20)

                id_ = re.findall("(id)-(\d{5,10})", url)[0][1]

                tipo_xpath = str_flat('''
                    //*[@class="price__title"] |
                    //*[contains(@class,"info__business-type")]
                ''')

                tipo = driverw.until(
                    EC.visibility_of_element_located((By.XPATH, tipo_xpath))
                ).text


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
                    driverw.until(
                        EC.visibility_of_element_located((By.XPATH, img_xpath))
                    )

                    imagens = driver.find_elements(By.XPATH, img_xpath)

                    imagens = [img.get_attribute("src") for img in imagens]
                except TimeoutException:
                    imagens = []

                sucesso, tentativa = False, 1
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


                while not sucesso and tentativa <= 10:
                    pass_cookie(driver)
                    
                    try:
                        driverw.until(
                            EC.element_to_be_clickable((By.XPATH, botao_xpath))
                        ).click()

                        iframe = driverw.until(
                            EC.element_to_be_clickable((By.XPATH, glink_iframe_xpath))
                        )

                        driver.switch_to.frame(iframe)

                        glink = driverw.until(
                            EC.visibility_of_element_located((By.XPATH, glink_xpath))
                        ).get_attribute("href")

                        latlng = re.findall("(.\d{2}\.\d{4,6})", glink)
                        lat, lng = float(latlng[0]), float(latlng[1])
                        sucesso = True

                    except Exception as e:
                        tentativa += 1
                        print(f"retry {tentativa}: {url}")
                        get_sleep(driver, url, 10)

                    finally:
                        driver.switch_to.default_content()

                if not sucesso:
                    print(f"latlong não encontrada: {session_id} {url}")

                line = {
                    "id": id_,
                    "origem": "zap" if "zap" in url else "vivareal",
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
        
            except Exception as e:
                print(e)
                print(session_id, " ", url)
