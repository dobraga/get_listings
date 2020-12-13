from concurrent.futures import ProcessPoolExecutor
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver import Chrome
from pyvirtualdisplay import Display
from os.path import join, exists
from retry import retry
from time import sleep
from tqdm import tqdm
import pandas as pd
from .aux import *
import jsonlines
import re



class Imoveis:
    def __init__(self, conf):
        self.conf = conf
        self.dir_webdriver = conf["dir_webdriver"]
        self.max_page = int(conf["max_page"])
        self.visible = conf["teste"]
        self.output = conf.get("output") or join(conf["dir_input"], "imoveis.jsonlines")
      
        self.base_url = [self.make_url(conf, site) for site in conf["site"]]

        if exists(self.output):
            self.urls_extraidas = pd.read_json(self.output, lines=True).url.to_list()
        else:
            self.urls_extraidas = []

        print("Páginas iniciais: ", self.base_url)

    def make_url(self, conf, site):
        with Display(visible=self.visible, size=(1600, 1024)):
            with Chrome(self.dir_webdriver) as driver:
                driver.maximize_window()

                url = conf[site]["url"]
                local = conf["local"]
                tipo_contrato = conf[site]["tipo_contrato"]
                tipo_propriedade = conf[site]["tipo_propriedade"]

                get_with_retry(driver, url)
                sleep(5)


                # popup de cookies
                iframe = get_if_exists(
                    driver, '//iframe[@name="mtm-frame-prompt"]'
                )

                if iframe:
                    driver.switch_to.frame(iframe)
                    button = get_if_exists(driver, '//button[text()="Sim"]')
                    if button:
                        button.click()
                    driver.switch_to.default_content()
                    sleep(1)


                # Seleciona o tipo de contrato
                select_tipo_contrato = get_if_exists(
                    driver, '//select[@class="js-select-business"]/option[contains(text(), "{}")]'.format(tipo_contrato)
                ) or get_if_exists(
                    driver, '//div[@class="business-filter__container"]/button[@title="{}"]'.format(tipo_contrato)
                ) or get_if_exists(
                    driver, '//ul[@class="operation-type-menu"]//p[contains(text(), "{}")]'.format("Comprar")
                )

                if select_tipo_contrato:
                    select_tipo_contrato.click()


                # Seleciona o tipo da propriedade
                seletor_tipo_propriedade = get_if_exists(
                    driver, '//select[@class="js-select-type"]'
                ) or get_if_exists(
                    driver, '//select[@class="l-select__item l-select__input"]'
                ) or get_if_exists(
                    driver, '//div[@class="property-type-container"]'
                )

                if seletor_tipo_propriedade:
                    seletor_tipo_propriedade.click()


                select_tipo_propriedade = get_if_exists(
                    driver, '//select[@class="js-select-type"]//option[contains(text(), "{}")]'.format(tipo_propriedade)
                ) or get_if_exists(
                    driver, '//select[@class="l-select__item l-select__input"]//option[contains(text(), "{}")]'.format(tipo_propriedade)
                ) or get_if_exists(
                    driver, '//div[@class="property-type-container"]//div[contains(text(), "{}")]'.format(tipo_propriedade)
                )

                if select_tipo_propriedade:
                    select_tipo_propriedade.click()


                # Seleciona o local
                select_local = get_if_exists(
                    driver, '//input[@id="filter-location-search-input"]'
                ) or get_if_exists(
                    driver, '//input[@class="typeahead__input js-typeahead-input"]'
                ) or get_if_exists(
                    driver, '//div[@class="search-box-container"]//input'
                )

                if select_local:
                    select_local.send_keys(local)
                    sleep(3)
                    select_local.send_keys(Keys.ENTER)


                # Buscar
                buscar = get_if_exists(
                    driver, '//button[@class="hero-filters__cta js-filters-cta button button-primary button-primary--standard button--regular"]'
                ) or get_if_exists(
                    driver, '//button[@data-qa="search-button"]'
                )

                if buscar:
                    buscar.click()

                sleep(3)
                return driver.current_url


    def run(self):
        with ProcessPoolExecutor() as exe:            
            paginas = exe.map(self.get_paginas, self.base_url)
            paginas = flat(list(paginas))
            print(f"Buscando um total de {len(paginas)} páginas")

            imoveis = exe.map(self.get_imoveis, paginas)
            imoveis = flat(list(imoveis))
            imoveis = list(filter(lambda x: x not in self.urls_extraidas, imoveis))

            print(f"Buscando um total de {len(imoveis)} imóveis")

            _ = tqdm(exe.map(self.parse_imovel, imoveis), total=len(imoveis))
    

    @retry(tries=3)
    def get_paginas(self, base_url):
        paginas = []
        paginas.append(base_url)

        with Display(visible=self.visible, size=(1600, 1024)):
            with Chrome(self.dir_webdriver) as driver:
                get_with_retry(driver, base_url)

                while len(paginas) < self.max_page:
                    proxima_pagina = driver.find_elements(
                        By.XPATH, '//a[@title="Próxima página"]'
                    ) or driver.find_elements(
                        By.XPATH, '//button[@aria-label="Próxima Página"]'
                    ) or driver.find_elements(
                        By.XPATH, '//*[@id="react-paging"]/div/ul/li[6]/a'
                    )

                    if proxima_pagina:
                        u = driver.current_url
                        while u == driver.current_url:
                            try:
                                proxima_pagina[0].click()
                            except:
                                sleep(0.5)
                        sleep(1)
                        paginas.append(driver.current_url)

                    else:
                        break

                return paginas


    @retry(tries=3)
    def get_imoveis(self, url):
        with Display(visible=self.visible, size=(1600, 1024)):
            with Chrome(self.dir_webdriver) as driver:
                get_with_retry(driver, url)
                sleep(1)

                botoes = driver.find_elements(
                    By.XPATH,
                    '//div[@class="results-list js-results-list"]//a[@class="property-card__content-link js-card-title"]',
                ) or driver.find_elements(By.XPATH, '//div[@class="card-container"]')

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
                                get_with_retry(driver, url)

                            botao = driver.find_elements_by_xpath(xpath)[idx]
                            try:
                                botao.click()
                                driver.switch_to.window(driver.window_handles[-1])
                                sleep(1)
                                u = driver.current_url
                            except:
                                pass

                            tentativa += 1
                            driver.switch_to.window(driver.window_handles[0])

                        return u

                    links = [
                        click_get_link(driver, '//div[@class="card-container"]', idx)
                        for idx in range(len(botoes))
                    ]

                return links

    @retry(tries=5)
    def parse_imovel(self, url, mode="rw"):
        with Display(visible=self.visible, size=(1600, 1024)):
            with Chrome(self.dir_webdriver) as driver:
                driver.maximize_window()
                get_with_retry(driver, url)

                id_ = re.findall("(id)-(\d{5,10})", url)[0][1]

                tipo = get(driver, '//*[@class="price__title"]') or get(
                    driver, '//*[@class="info__business-type color-dark text-regular"]'
                )

                title = get(driver, '//*[@class="title__title js-title-view"]') or get(
                    driver,
                    '//*[@class="main__info--title heading-large heading-large__bold align-left"]',
                )

                endereco = get(driver, '//*[@class="title__address js-address"]') or get(
                    driver, "//article[1]/div/div[1]/div[1]/p/button/span[2]",
                )

                metragem = get(
                    driver, '//*[@class="features__item features__item--area js-area"]', True,
                ) or get(driver, '//*[@class="feature__item text-regular js-areas"]', True)

                quartos = get(
                    driver,
                    '//*[@class="features__item features__item--bedroom js-bedrooms"]',
                    True,
                ) or get(driver, '//*[@class="feature__item text-regular js-bedrooms"]', True)

                banheiros = get(
                    driver,
                    '//*[@class="features__item features__item--bathroom js-bathrooms"]/span',
                    True,
                ) or get(driver, '//*[@class="feature__item text-regular js-bathrooms"]', True,)

                vagas = get(
                    driver, '//*[@class="features__item features__item--parking js-parking"]', True,
                ) or get(
                    driver, '//*[@class="feature__item text-regular js-parking-spaces"]', True,
                )

                desc = driver.find_elements(
                    By.XPATH, '//*[@class="description__text"]'
                ) or driver.find_elements(
                    By.XPATH, '//*[@class="amenities__description text-regular text-margin-zero"]',
                )

                desc = " ".join([d.text for d in desc])

                preco = get(
                    driver, '//*[@class="price__price-info js-price-sale"][last()]', True,
                ) or get(
                    driver,
                    '//*[@class="price__item--main text-regular text-regular__bolder"][last()]',
                    True,
                )

                condominio = get(
                    driver, '//*[@class="price__list-value condominium js-condominium"]', True,
                ) or get(
                    driver, '//*[@class="price__item condominium color-dark text-regular"]', True,
                )

                imagens = driver.find_elements(
                    By.XPATH, '//li[@class="carousel__slide js-carousel-item-wrapper"]/img',
                ) or driver.find_elements(
                    By.XPATH, '//li[@class="js-carousel-item carousel__item"]/img',
                )

                imagens = [img.get_attribute("src") for img in imagens]

                sucesso, click, tentativa = False, False, 1
                message, glink, lat, lng = "", "", "", ""

                botao_xpath = [
                    '//div[@class="box--display-flex box--items-baseline"]//button',
                    '//button[@class="map__navigate js-navigate"]',
                ]
                glink_iframe_xpath = [
                    '//*[@id="listing-map"]/article/iframe',
                    '//*[@id="js-site-main"]//iframe',
                ]
                glink_xpath = [
                    '//*[@id="mapDiv"]/div/div/div[8]/div/div/div/div[7]/div/a[contains(@href,"")]',
                    '//*[@id="mapDiv"]//div[@class="google-maps-link"]/a[contains(@href,"")]'
                ]
    

                while not sucesso and tentativa <= 50:
                    if tentativa % 10 == 0:
                        print(f"retry {tentativa}: {url}")
                        get_with_retry(driver, url)

                    try:
                        botao = get_if_exists(driver, botao_xpath[0]) or get_if_exists(
                            driver, botao_xpath[1]
                        )
                        if botao:
                            botao.click()
                            sleep(2)
                    except:
                        pass

                    iframe = get_if_exists(
                        driver, glink_iframe_xpath[0]
                    ) or get_if_exists(driver, glink_iframe_xpath[1])

                    if iframe:
                        driver.switch_to.frame(iframe)
                        sleep(3)
                        glink = get_if_exists(driver, glink_xpath[0]) or get_if_exists(
                            driver, glink_xpath[1]
                        )

                        if glink:
                            glink = glink.get_attribute("href")
                            latlng = re.findall("(.\d{2}\.\d{4,6})", glink)
                            if len(latlng) >= 2:
                                lat, lng = float(latlng[0]), float(latlng[1])
                                sucesso = True

                        driver.switch_to.default_content()

                    if not sucesso:
                        sleep(1)
                        tentativa += 1

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
        if "r" in mode:
            return line
    